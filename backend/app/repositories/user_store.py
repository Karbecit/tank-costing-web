import hashlib
import os
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any

import pyotp

from app.auth.passwords import hash_password, validate_password, verify_password
from app.database import get_connection

AUTH_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    display_name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'editor',
    is_active INTEGER NOT NULL DEFAULT 1,
    mfa_secret TEXT,
    mfa_enabled INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS trusted_devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    user_agent TEXT,
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_id INTEGER REFERENCES users(id),
    action TEXT NOT NULL,
    target_type TEXT,
    target_id TEXT,
    detail TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_log(created_at DESC);
"""

TRUST_DAYS = int(os.getenv("TRUST_DEVICE_DAYS", "90"))


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def init_auth_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(AUTH_SCHEMA)
    user_cols = {row[1] for row in conn.execute("PRAGMA table_info(users)").fetchall()}
    if "mfa_secret" not in user_cols:
        conn.execute("ALTER TABLE users ADD COLUMN mfa_secret TEXT")
    if "mfa_enabled" not in user_cols:
        conn.execute("ALTER TABLE users ADD COLUMN mfa_enabled INTEGER NOT NULL DEFAULT 0")


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def public_user(row: dict) -> dict:
    return {
        "id": row["id"],
        "email": row["email"],
        "display_name": row["display_name"],
        "role": row["role"],
        "is_active": bool(row["is_active"]),
        "mfa_enabled": bool(row.get("mfa_enabled")),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def bootstrap_admin() -> None:
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"]
    if count > 0:
        return
    email = os.getenv("ADMIN_EMAIL", "admin@local")
    password = os.getenv("ADMIN_PASSWORD", "ChangeMe123!")
    create_user(
        {
            "email": email,
            "display_name": "Administrator",
            "password": password,
            "role": "admin",
        },
        skip_validation=True,
    )


def get_user(user_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return row_to_dict(row) if row else None


def get_user_by_email(email: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ? COLLATE NOCASE", (email.strip(),)
        ).fetchone()
    return row_to_dict(row) if row else None


def list_users() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM users ORDER BY email").fetchall()
    return [public_user(row_to_dict(r)) for r in rows]


def authenticate(email: str, password: str) -> dict | None:
    user = get_user_by_email(email)
    if not user or not user["is_active"]:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user


def create_user(data: dict, skip_validation: bool = False) -> dict:
    if not skip_validation:
        validate_password(data["password"])
    now = utc_now()
    pw_hash = hash_password(data["password"])
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO users (
                email, display_name, password_hash, role, is_active,
                mfa_secret, mfa_enabled, created_at, updated_at
            ) VALUES (?, ?, ?, ?, 1, NULL, 0, ?, ?)
            """,
            (
                data["email"].strip().lower(),
                data["display_name"].strip(),
                pw_hash,
                data.get("role", "editor"),
                now,
                now,
            ),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()
    return public_user(row_to_dict(row))


def update_user(user_id: int, data: dict) -> dict | None:
    existing = get_user(user_id)
    if not existing:
        return None
    now = utc_now()
    fields = []
    params: list[Any] = []
    if "display_name" in data and data["display_name"] is not None:
        fields.append("display_name = ?")
        params.append(data["display_name"].strip())
    if "role" in data and data["role"] is not None:
        fields.append("role = ?")
        params.append(data["role"])
    if "is_active" in data and data["is_active"] is not None:
        fields.append("is_active = ?")
        params.append(1 if data["is_active"] else 0)
    if not fields:
        return public_user(existing)
    fields.append("updated_at = ?")
    params.append(now)
    params.append(user_id)
    with get_connection() as conn:
        conn.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = ?", params)
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return public_user(row_to_dict(row))


def change_password(user_id: int, current: str, new_password: str) -> bool:
    user = get_user(user_id)
    if not user or not verify_password(current, user["password_hash"]):
        return False
    validate_password(new_password)
    now = utc_now()
    with get_connection() as conn:
        cur = conn.execute(
            "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
            (hash_password(new_password), now, user_id),
        )
        conn.commit()
        return cur.rowcount > 0


def reset_password(user_id: int, password: str) -> bool:
    validate_password(password)
    now = utc_now()
    with get_connection() as conn:
        cur = conn.execute(
            "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
            (hash_password(password), now, user_id),
        )
        conn.commit()
        return cur.rowcount > 0


def begin_mfa_setup(user_id: int) -> dict:
    secret = pyotp.random_base32()
    now = utc_now()
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET mfa_secret = ?, mfa_enabled = 0, updated_at = ? WHERE id = ?",
            (secret, now, user_id),
        )
        conn.commit()
    user = get_user(user_id)
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=user["email"], issuer_name="Tank Costing")
    return {"secret": secret, "otpauth_uri": uri}


def confirm_mfa(user_id: int, code: str) -> bool:
    user = get_user(user_id)
    if not user or not user.get("mfa_secret"):
        return False
    if not pyotp.TOTP(user["mfa_secret"]).verify(code, valid_window=1):
        return False
    now = utc_now()
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET mfa_enabled = 1, updated_at = ? WHERE id = ?",
            (now, user_id),
        )
        conn.commit()
    return True


def disable_mfa(user_id: int) -> None:
    now = utc_now()
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE users SET mfa_secret = NULL, mfa_enabled = 0, updated_at = ?
            WHERE id = ?
            """,
            (now, user_id),
        )
        conn.execute("DELETE FROM trusted_devices WHERE user_id = ?", (user_id,))
        conn.commit()


def verify_mfa_code(user_id: int, code: str) -> bool:
    user = get_user(user_id)
    if not user or not user.get("mfa_secret") or not user.get("mfa_enabled"):
        return False
    return pyotp.TOTP(user["mfa_secret"]).verify(code, valid_window=1)


def needs_mfa(user: dict, trusted_token: str | None) -> bool:
    if not user.get("mfa_enabled") or not user.get("mfa_secret"):
        return False
    if user["role"] == "admin":
        return True
    if trusted_token and verify_trusted_device(user["id"], trusted_token):
        return False
    return True


def create_trusted_device(user_id: int, user_agent: str | None) -> str:
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    now = utc_now()
    expires = (datetime.now(timezone.utc) + timedelta(days=TRUST_DAYS)).replace(microsecond=0)
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO trusted_devices (user_id, token_hash, user_agent, expires_at, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, token_hash, user_agent, expires.isoformat(), now),
        )
        conn.commit()
    return token


def verify_trusted_device(user_id: int, token: str) -> bool:
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id FROM trusted_devices
            WHERE user_id = ? AND token_hash = ? AND expires_at > ?
            """,
            (user_id, token_hash, now),
        ).fetchone()
    return row is not None


def write_audit(
    actor_id: int | None,
    action: str,
    target_type: str | None = None,
    target_id: str | None = None,
    detail: str | None = None,
) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO audit_log (actor_id, action, target_type, target_id, detail, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (actor_id, action, target_type, target_id, detail, utc_now()),
        )
        conn.commit()


def list_audit(limit: int = 100) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT a.*, u.email AS actor_email
            FROM audit_log a
            LEFT JOIN users u ON u.id = a.actor_id
            ORDER BY a.created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [row_to_dict(r) for r in rows]
