"""App settings persisted in SQLite (SMTP etc.)."""

from __future__ import annotations

import os
from typing import Any

from app.database import get_connection

SMTP_KEYS = (
    "smtp_host",
    "smtp_port",
    "smtp_user",
    "smtp_password",
    "smtp_from",
    "smtp_use_tls",
    "app_base_url",
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def init_settings_schema(conn) -> None:
    conn.executescript(SCHEMA)


def _get(key: str) -> str | None:
    with get_connection() as conn:
        row = conn.execute("SELECT value FROM app_settings WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else None


def _set(key: str, value: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO app_settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (key, value),
        )
        conn.commit()


def get_smtp_settings() -> dict[str, Any]:
    """Return SMTP config; env vars override stored values when set."""
    stored = {k: _get(k) for k in SMTP_KEYS}
    env_map = {
        "smtp_host": os.getenv("SMTP_HOST"),
        "smtp_port": os.getenv("SMTP_PORT"),
        "smtp_user": os.getenv("SMTP_USER"),
        "smtp_password": os.getenv("SMTP_PASSWORD"),
        "smtp_from": os.getenv("SMTP_FROM"),
        "smtp_use_tls": os.getenv("SMTP_USE_TLS"),
        "app_base_url": os.getenv("APP_BASE_URL"),
    }
    merged: dict[str, Any] = {}
    for key in SMTP_KEYS:
        env_val = env_map.get(key)
        if env_val is not None and env_val != "":
            merged[key] = env_val
        else:
            merged[key] = stored.get(key)
    if merged.get("smtp_port") is not None:
        merged["smtp_port"] = int(merged["smtp_port"])
    if merged.get("smtp_use_tls") is not None:
        val = str(merged["smtp_use_tls"]).lower()
        merged["smtp_use_tls"] = val in ("1", "true", "yes")
    return merged


def get_smtp_public() -> dict[str, Any]:
    """SMTP settings safe for admin UI (password masked)."""
    cfg = get_smtp_settings()
    has_password = bool(cfg.get("smtp_password"))
    return {
        "smtp_host": cfg.get("smtp_host") or "",
        "smtp_port": int(cfg.get("smtp_port") or 587),
        "smtp_user": cfg.get("smtp_user") or "",
        "smtp_from": cfg.get("smtp_from") or "",
        "smtp_use_tls": bool(cfg.get("smtp_use_tls", True)),
        "app_base_url": cfg.get("app_base_url") or "",
        "password_set": has_password,
        "configured": bool(cfg.get("smtp_host") and cfg.get("smtp_from")),
    }


def save_smtp_settings(data: dict[str, Any]) -> dict[str, Any]:
    for key in ("smtp_host", "smtp_port", "smtp_user", "smtp_from", "app_base_url"):
        if key in data and data[key] is not None:
            _set(key, str(data[key]))
    if "smtp_use_tls" in data:
        _set("smtp_use_tls", "1" if data["smtp_use_tls"] else "0")
    if data.get("smtp_password"):
        _set("smtp_password", str(data["smtp_password"]))
    return get_smtp_public()
