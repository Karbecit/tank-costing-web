from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import CurrentUser, require_role
from app.repositories import user_store
from app.schemas.auth import UserPublic
from app.schemas.user import PasswordReset, UserCreate, UserUpdate

router = APIRouter(prefix="/api/admin/users", tags=["admin"])


@router.get("", response_model=list[UserPublic])
def list_users(_admin: Annotated[CurrentUser, Depends(require_role("admin"))]):
    return [UserPublic(**u) for u in user_store.list_users()]


@router.post("", response_model=UserPublic, status_code=201)
def create_user(
    body: UserCreate,
    admin: Annotated[CurrentUser, Depends(require_role("admin"))],
):
    if user_store.get_user_by_email(body.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    try:
        user = user_store.create_user(body.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    user_store.write_audit(admin.id, "user.create", "user", str(user["id"]), body.email)
    return UserPublic(**user)


@router.put("/{user_id}", response_model=UserPublic)
def update_user(
    user_id: int,
    body: UserUpdate,
    admin: Annotated[CurrentUser, Depends(require_role("admin"))],
):
    row = user_store.update_user(user_id, body.model_dump(exclude_unset=True))
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    user_store.write_audit(admin.id, "user.update", "user", str(user_id))
    return UserPublic(**row)


@router.post("/{user_id}/reset-password", status_code=204)
def reset_password(
    user_id: int,
    body: PasswordReset,
    admin: Annotated[CurrentUser, Depends(require_role("admin"))],
):
    try:
        ok = user_store.reset_password(user_id, body.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    user_store.write_audit(admin.id, "user.reset_password", "user", str(user_id))
