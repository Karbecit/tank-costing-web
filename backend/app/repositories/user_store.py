import os
import sqlite3
from datetime import datetime, timezone
from typing import Any

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
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
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
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def init_auth_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(AUTH_SCHEMA)


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def public_user(row: dict) -> dict:
    return {
        "id": row["id"],
        "email": row["email"],
        "display_name": row["display_name"],
        "role": row["role"],
        "is_active": bool(row["is_active"]),
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
                email, display_name, password_hash, role, is_active, created_at, updated_at
            ) VALUES (?, ?, ?, ?, 1, ?, ?)
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
