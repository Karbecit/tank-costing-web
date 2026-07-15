import os
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB = ROOT / "data" / "tankcosting.db"
DB_PATH = Path(os.getenv("DATABASE_PATH", str(DEFAULT_DB)))
if not DB_PATH.is_absolute():
    DB_PATH = ROOT / DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grade TEXT NOT NULL,
    thickness REAL NOT NULL,
    width INTEGER NOT NULL,
    price_kg REAL NOT NULL,
    weight_cum REAL,
    UNIQUE(grade, thickness, width)
);

CREATE TABLE IF NOT EXISTS stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sort TEXT,
    type TEXT,
    description TEXT,
    details TEXT,
    cost REAL DEFAULT 0,
    hours INTEGER DEFAULT 0,
    manufacturer TEXT,
    manuf_part_num TEXT,
    dated TEXT,
    revision_details TEXT,
    stock_num TEXT
);

CREATE TABLE IF NOT EXISTS status (
    stat_id INTEGER PRIMARY KEY,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS clients (
    client_id INTEGER PRIMARY KEY,
    company_name TEXT,
    contact_name TEXT,
    billing_address TEXT,
    town TEXT,
    state TEXT,
    postal_code TEXT,
    country TEXT,
    contact_title TEXT,
    phone_number TEXT,
    extension TEXT,
    fax_number TEXT,
    email_address TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS quote_num (
    id INTEGER PRIMARY KEY,
    number_quote TEXT,
    rev TEXT,
    stat_id INTEGER REFERENCES status(stat_id),
    client_id INTEGER REFERENCES clients(client_id),
    job_description TEXT,
    qty TEXT,
    originator TEXT,
    date TEXT,
    probability INTEGER,
    jma_contact TEXT,
    notes TEXT
);
"""


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA)
        conn.commit()
