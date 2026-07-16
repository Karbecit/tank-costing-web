import os
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwt_tokens import decode_access_token
from app.repositories import user_store

_bearer = HTTPBearer(auto_error=False)

ROLES_ORDER = {"viewer": 0, "editor": 1, "admin": 2}


class CurrentUser:
    def __init__(self, user_id: int, email: str, role: str, display_name: str):
        self.id = user_id
        self.email = email
        self.role = role
        self.display_name = display_name

    def has_role(self, minimum: str) -> bool:
        return ROLES_ORDER.get(self.role, -1) >= ROLES_ORDER.get(minimum, 99)


def auth_disabled() -> bool:
    return os.getenv("AUTH_DISABLED", "").lower() in ("1", "true", "yes")


def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> CurrentUser:
    if auth_disabled():
        return CurrentUser(0, "dev@local", "admin", "Dev User")
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        data = decode_access_token(creds.credentials)
        user_id = int(data["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from None

    row = user_store.get_user(user_id)
    if not row or not row["is_active"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive")
    return CurrentUser(
        user_id=row["id"],
        email=row["email"],
        role=row["role"],
        display_name=row["display_name"],
    )


def require_role(minimum: str):
    def _dep(user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
        if not user.has_role(minimum):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return user

    return _dep
