import os
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

ALGORITHM = "HS256"
ACCESS_HOURS = 8


def _secret() -> str:
    key = os.getenv("JWT_SECRET", "")
    if not key:
        key = "dev-only-change-in-production!!"
    return key


def create_access_token(user_id: int, email: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "typ": "access",
        "iat": now,
        "exp": now + timedelta(hours=ACCESS_HOURS),
    }
    return jwt.encode(payload, _secret(), algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    data = jwt.decode(token, _secret(), algorithms=[ALGORITHM])
    if data.get("typ") != "access":
        raise jwt.InvalidTokenError("Not an access token")
    return data
