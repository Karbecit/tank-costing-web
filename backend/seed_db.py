"""Seed SQLite database from legacy Access Excel exports."""

from __future__ import annotations

import os
import sys
from datetime import date, datetime
from pathlib import Path

import openpyxl
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from app.database import DB_PATH, get_connection, init_db  # noqa: E402

load_dotenv(ROOT.parent / ".env")


def _cell(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat(sep=" ", timespec="seconds")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str):
        cleaned = value.replace("_x000d_", "\n").strip()
        return cleaned or None
    return value


def _seed_dir() -> Path:
    configured = os.getenv("SEED_DATA_DIR")
    if configured:
        path = Path(configured)
        if not path.is_absolute():
            path = (ROOT.parent / path).resolve()
        return path
    return ROOT.parent.parent / "Old Program" / "Database doco"


def _load_sheet(path: Path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows = list(wb.active.iter_rows(values_only=True))
    wb.close()
    if not rows:
        return []
    headers = [str(h).strip() if h is not None else "" for h in rows[0]]
    records = []
    for row in rows[1:]:
        if all(v is None or str(v).strip() == "" for v in row):
            continue
        records.append({headers[i]: _cell(row[i]) for i in range(len(headers))})
    return records


def seed() -> None:
    seed_dir = _seed_dir()
    if not seed_dir.exists():
        raise FileNotFoundError(f"Seed data directory not found: {seed_dir}")

    init_db()
    with get_connection() as conn:
        conn.execute("DELETE FROM quote_num")
        conn.execute("DELETE FROM clients")
        conn.execute("DELETE FROM status")
        conn.execute("DELETE FROM stock")
        conn.execute("DELETE FROM rates")

        for row in _load_sheet(seed_dir / "Rates.xlsx"):
            conn.execute(
                """
                INSERT INTO rates (grade, thickness, width, price_kg, weight_cum)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    row.get("Grade"),
                    row.get("Thickness"),
                    row.get("Width"),
                    row.get("PriceKg"),
                    row.get("Weight/cum"),
                ),
            )

        for row in _load_sheet(seed_dir / "Stock.xlsx"):
            stock_num = row.get("Stock#") or row.get("Stock.")
            conn.execute(
                """
                INSERT INTO stock (
                    sort, type, description, details, cost, hours,
                    manufacturer, manuf_part_num, dated, revision_details, stock_num
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("Sort"),
                    row.get("Type"),
                    row.get("Description"),
                    row.get("Details"),
                    row.get("Cost") or 0,
                    row.get("Hours") or 0,
                    row.get("Manufacturer"),
                    row.get("Manuf part num"),
                    row.get("Dated"),
                    row.get("Revision details"),
                    stock_num,
                ),
            )

        for row in _load_sheet(seed_dir / "Status.xlsx"):
            conn.execute(
                "INSERT INTO status (stat_id, status) VALUES (?, ?)",
                (row.get("StatID"), row.get("Status")),
            )

        for row in _load_sheet(seed_dir / "Clients.xlsx"):
            conn.execute(
                """
                INSERT INTO clients (
                    client_id, company_name, contact_name, billing_address,
                    town, state, postal_code, country, contact_title,
                    phone_number, extension, fax_number, email_address, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("ClientID"),
                    row.get("CompanyName"),
                    row.get("ContactName"),
                    row.get("BillingAddress"),
                    row.get("Town"),
                    row.get("State"),
                    row.get("PostalCode"),
                    row.get("Country"),
                    row.get("ContactTitle"),
                    row.get("PhoneNumber"),
                    row.get("Extension"),
                    row.get("FaxNumber"),
                    row.get("EmailAddress"),
                    row.get("Notes"),
                ),
            )

        client_ids = {
            row[0]
            for row in conn.execute("SELECT client_id FROM clients").fetchall()
        }
        stat_ids = {
            row[0] for row in conn.execute("SELECT stat_id FROM status").fetchall()
        }

        for row in _load_sheet(seed_dir / "QuoteNum.xlsx"):
            client_id = row.get("ClientID")
            stat_id = row.get("StatID")
            if not client_id or client_id not in client_ids:
                client_id = None
            if not stat_id or stat_id not in stat_ids:
                stat_id = None
            conn.execute(
                """
                INSERT INTO quote_num (
                    id, number_quote, rev, stat_id, client_id, job_description,
                    qty, originator, date, probability, jma_contact, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("ID"),
                    row.get("NumberQuote"),
                    row.get("Rev"),
                    stat_id,
                    client_id,
                    row.get("JobDescription"),
                    row.get("Qty"),
                    row.get("Originator"),
                    row.get("Date"),
                    row.get("Probability"),
                    row.get("JMAContact"),
                    row.get("Notes"),
                ),
            )

        conn.commit()

    with get_connection() as conn:
        counts = {
            "rates": conn.execute("SELECT COUNT(*) FROM rates").fetchone()[0],
            "stock": conn.execute("SELECT COUNT(*) FROM stock").fetchone()[0],
            "clients": conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0],
            "quote_num": conn.execute("SELECT COUNT(*) FROM quote_num").fetchone()[0],
            "status": conn.execute("SELECT COUNT(*) FROM status").fetchone()[0],
        }

    print(f"Database seeded at {DB_PATH}")
    for name, count in counts.items():
        print(f"  {name}: {count}")


if __name__ == "__main__":
    seed()
