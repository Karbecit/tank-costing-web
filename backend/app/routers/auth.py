from typing import Annotated, Union

from fastapi import APIRouter, Cookie, Depends, Header, HTTPException, Response, status

from app.auth.dependencies import CurrentUser, get_current_user
from app.auth.jwt_tokens import (
    create_access_token,
    create_mfa_pending_token,
    decode_mfa_pending_token,
)
from app.repositories import user_store
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    MfaConfirmRequest,
    MfaRequiredResponse,
    MfaSetupResponse,
    MfaVerifyRequest,
    UserPublic,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])

TRUST_COOKIE = "tc_trust"
TRUST_MAX_AGE = user_store.TRUST_DAYS * 86400


def _login_response(user: dict) -> LoginResponse:
    token = create_access_token(user["id"], user["email"], user["role"])
    return LoginResponse(
        access_token=token,
        user=UserPublic(**user_store.public_user(user)),
    )


@router.post("/login", response_model=Union[LoginResponse, MfaRequiredResponse])
def login(
    body: LoginRequest,
    tc_trust: Annotated[str | None, Cookie()] = None,
):
    user = user_store.authenticate(body.email, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    if user_store.needs_mfa(user, tc_trust):
        return MfaRequiredResponse(
            mfa_token=create_mfa_pending_token(user["id"]),
            trust_allowed=user["role"] != "admin",
        )
    return _login_response(user)


@router.post("/mfa/verify", response_model=LoginResponse)
def mfa_verify(
    body: MfaVerifyRequest,
    response: Response,
    user_agent: Annotated[str | None, Header()] = None,
):
    try:
        data = decode_mfa_pending_token(body.mfa_token)
        user_id = int(data["sub"])
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired MFA session") from exc

    user = user_store.get_user(user_id)
    if not user or not user["is_active"]:
        raise HTTPException(status_code=401, detail="User not found")
    if not user_store.verify_mfa_code(user_id, body.code):
        raise HTTPException(status_code=401, detail="Invalid authentication code")

    if body.trust_device and user["role"] != "admin":
        token = user_store.create_trusted_device(user_id, user_agent)
        response.set_cookie(
            TRUST_COOKIE,
            token,
            max_age=TRUST_MAX_AGE,
            httponly=True,
            samesite="lax",
            secure=False,
        )
    return _login_response(user)


@router.get("/me", response_model=UserPublic)
def me(user: Annotated[CurrentUser, Depends(get_current_user)]):
    row = user_store.get_user(user.id)
    if not row:
        raise HTTPException(status_code=401, detail="User not found")
    return UserPublic(**user_store.public_user(row))


@router.post("/change-password", status_code=204)
def change_password(
    body: ChangePasswordRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    try:
        ok = user_store.change_password(user.id, body.current_password, body.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not ok:
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user_store.write_audit(user.id, "user.change_password", "user", str(user.id))


@router.post("/mfa/setup", response_model=MfaSetupResponse)
def mfa_setup(user: Annotated[CurrentUser, Depends(get_current_user)]):
    return MfaSetupResponse(**user_store.begin_mfa_setup(user.id))


@router.post("/mfa/confirm", status_code=204)
def mfa_confirm(
    body: MfaConfirmRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    if not user_store.confirm_mfa(user.id, body.code):
        raise HTTPException(status_code=400, detail="Invalid code — check your authenticator app")
    user_store.write_audit(user.id, "user.mfa_enable", "user", str(user.id))


@router.post("/mfa/disable", status_code=204)
def mfa_disable(
    body: MfaConfirmRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    if not user_store.verify_mfa_code(user.id, body.code):
        raise HTTPException(status_code=400, detail="Invalid code")
    user_store.disable_mfa(user.id)
    user_store.write_audit(user.id, "user.mfa_disable", "user", str(user.id))
