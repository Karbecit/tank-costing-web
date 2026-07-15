import json
import sqlite3
from datetime import datetime, timezone
from typing import Any

from app.database import get_connection

SCHEMA_EXTENSIONS = """
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    contact_name TEXT,
    email TEXT,
    phone TEXT,
    billing_address TEXT,
    delivery_address TEXT,
    town TEXT,
    state TEXT,
    postal_code TEXT,
    country TEXT DEFAULT 'Australia',
    notes TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS costings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    customer_id INTEGER REFERENCES customers(id),
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_costings_updated ON costings(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_customers_company ON customers(company_name);
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def init_extended_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_EXTENSIONS)


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def list_customers(limit: int = 100, offset: int = 0, q: str | None = None) -> list[dict]:
    query = "SELECT * FROM customers"
    params: list[Any] = []
    if q:
        query += " WHERE company_name LIKE ? OR contact_name LIKE ? OR email LIKE ?"
        like = f"%{q.strip()}%"
        params.extend([like, like, like])
    query += " ORDER BY company_name LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [row_to_dict(r) for r in rows]


def get_customer(customer_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
    return row_to_dict(row) if row else None


def create_customer(data: dict) -> dict:
    now = utc_now()
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO customers (
                company_name, contact_name, email, phone,
                billing_address, delivery_address, town, state, postal_code,
                country, notes, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["company_name"],
                data.get("contact_name"),
                data.get("email"),
                data.get("phone"),
                data.get("billing_address"),
                data.get("delivery_address"),
                data.get("town"),
                data.get("state"),
                data.get("postal_code"),
                data.get("country") or "Australia",
                data.get("notes"),
                now,
                now,
            ),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM customers WHERE id = ?", (cur.lastrowid,)).fetchone()
    return row_to_dict(row)


def update_customer(customer_id: int, data: dict) -> dict | None:
    existing = get_customer(customer_id)
    if not existing:
        return None
    now = utc_now()
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE customers SET
                company_name = ?, contact_name = ?, email = ?, phone = ?,
                billing_address = ?, delivery_address = ?, town = ?, state = ?,
                postal_code = ?, country = ?, notes = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                data.get("company_name", existing["company_name"]),
                data.get("contact_name", existing.get("contact_name")),
                data.get("email", existing.get("email")),
                data.get("phone", existing.get("phone")),
                data.get("billing_address", existing.get("billing_address")),
                data.get("delivery_address", existing.get("delivery_address")),
                data.get("town", existing.get("town")),
                data.get("state", existing.get("state")),
                data.get("postal_code", existing.get("postal_code")),
                data.get("country", existing.get("country")),
                data.get("notes", existing.get("notes")),
                now,
                customer_id,
            ),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
    return row_to_dict(row)


def delete_customer(customer_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        conn.commit()
        return cur.rowcount > 0


def list_costings(limit: int = 50, offset: int = 0) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT c.id, c.title, c.customer_id, c.created_at, c.updated_at,
                   cu.company_name AS customer_name
            FROM costings c
            LEFT JOIN customers cu ON cu.id = c.customer_id
            ORDER BY c.updated_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()
    return [row_to_dict(r) for r in rows]


def get_costing(costing_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT c.*, cu.company_name AS customer_name
            FROM costings c
            LEFT JOIN customers cu ON cu.id = c.customer_id
            WHERE c.id = ?
            """,
            (costing_id,),
        ).fetchone()
    if not row:
        return None
    data = row_to_dict(row)
    data["payload"] = json.loads(data["payload"])
    return data


def save_costing(
    title: str,
    payload: dict,
    customer_id: int | None = None,
    costing_id: int | None = None,
) -> dict | None:
    now = utc_now()
    body = json.dumps(payload)
    with get_connection() as conn:
        if costing_id:
            existing = conn.execute(
                "SELECT id FROM costings WHERE id = ?", (costing_id,)
            ).fetchone()
            if not existing:
                return None
            conn.execute(
                """
                UPDATE costings SET title = ?, customer_id = ?, payload = ?, updated_at = ?
                WHERE id = ?
                """,
                (title, customer_id, body, now, costing_id),
            )
            cid = costing_id
        else:
            cur = conn.execute(
                """
                INSERT INTO costings (title, customer_id, payload, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (title, customer_id, body, now, now),
            )
            cid = cur.lastrowid
        conn.commit()
    result = get_costing(int(cid))
    return result


def delete_costing(costing_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM costings WHERE id = ?", (costing_id,))
        conn.commit()
        return cur.rowcount > 0
