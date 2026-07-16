from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import CurrentUser, require_role
from app.repositories import settings_store, user_store
from app.schemas.auth import AuditEntry, UserPublic
from app.schemas.settings import (
    SendInviteRequest,
    SmtpSettingsPublic,
    SmtpSettingsUpdate,
    SmtpTestRequest,
)
from app.schemas.user import PasswordReset, UserCreate, UserUpdate
from app.services import email_templates
from app.services.email_service import EmailError, send_email

router = APIRouter(prefix="/api/admin", tags=["admin"])
_admin = Annotated[CurrentUser, Depends(require_role("admin"))]


def _login_url() -> str:
    cfg = settings_store.get_smtp_settings()
    base = (cfg.get("app_base_url") or "http://localhost:5173").rstrip("/")
    return base


@router.get("/settings/smtp", response_model=SmtpSettingsPublic)
def get_smtp_settings(_admin: _admin):
    return SmtpSettingsPublic(**settings_store.get_smtp_public())


@router.put("/settings/smtp", response_model=SmtpSettingsPublic)
def update_smtp_settings(body: SmtpSettingsUpdate, admin: _admin):
    saved = settings_store.save_smtp_settings(body.model_dump())
    user_store.write_audit(admin.id, "settings.smtp_update", "settings", "smtp")
    return SmtpSettingsPublic(**saved)


@router.post("/settings/smtp/test", status_code=204)
def test_smtp(body: SmtpTestRequest, admin: _admin):
    subject, text = email_templates.smtp_test(recipient=body.to)
    try:
        send_email(to=body.to, subject=subject, body=text)
    except EmailError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    user_store.write_audit(admin.id, "settings.smtp_test", "settings", "smtp", body.to)


@router.get("/users", response_model=list[UserPublic])
def list_users(_admin: _admin):
    return [UserPublic(**u) for u in user_store.list_users()]


@router.get("/audit", response_model=list[AuditEntry])
def list_audit(_admin: _admin, limit: int = 100):
    return [AuditEntry(**row) for row in user_store.list_audit(limit=limit)]


@router.post("/users", response_model=UserPublic, status_code=201)
def create_user(body: UserCreate, admin: _admin):
    if user_store.get_user_by_email(body.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    try:
        user = user_store.create_user(body.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    user_store.write_audit(admin.id, "user.create", "user", str(user["id"]), body.email)
    return UserPublic(**user)


@router.put("/users/{user_id}", response_model=UserPublic)
def update_user(user_id: int, body: UserUpdate, admin: _admin):
    row = user_store.update_user(user_id, body.model_dump(exclude_unset=True))
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    user_store.write_audit(admin.id, "user.update", "user", str(user_id))
    return UserPublic(**row)


@router.post("/users/{user_id}/reset-password", status_code=204)
def reset_password(user_id: int, body: PasswordReset, admin: _admin):
    try:
        ok = user_store.reset_password(user_id, body.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    user_store.write_audit(admin.id, "user.reset_password", "user", str(user_id))


@router.post("/users/{user_id}/send-invite", status_code=204)
def send_user_invite(user_id: int, body: SendInviteRequest, admin: _admin):
    row = user_store.get_user(user_id)
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    password = body.password
    if not password:
        raise HTTPException(status_code=400, detail="Password required for invite email")
    subject, text = email_templates.user_invite(
        display_name=row["display_name"],
        email=row["email"],
        password=password,
        login_url=_login_url(),
    )
    try:
        send_email(to=row["email"], subject=subject, body=text)
    except EmailError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    user_store.write_audit(admin.id, "user.send_invite", "user", str(user_id), row["email"])
