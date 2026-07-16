from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import CurrentUser, get_current_user
from app.auth.jwt_tokens import create_access_token
from app.repositories import user_store
from app.schemas.auth import LoginRequest, LoginResponse, UserPublic

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest):
    user = user_store.authenticate(body.email, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    token = create_access_token(user["id"], user["email"], user["role"])
    return LoginResponse(
        access_token=token,
        user=UserPublic(**user_store.public_user(user)),
    )


@router.get("/me", response_model=UserPublic)
def me(user: Annotated[CurrentUser, Depends(get_current_user)]):
    row = user_store.get_user(user.id)
    if not row:
        raise HTTPException(status_code=401, detail="User not found")
    return UserPublic(**user_store.public_user(row))
