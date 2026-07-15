# Database

## Engine

SQLite for local development: `data/tankcosting.db` (gitignored).

## Tables

### rates (from Coil2000.mdb)

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | Auto |
| grade | TEXT | e.g. 304, 316 |
| thickness | REAL | mm |
| width | INTEGER | mm |
| price_kg | REAL | AUD per kg |
| weight_cum | REAL | kg/m³ |

**238 rows** from `Rates.xlsx`

### stock (from Components2000.mdb)

| Column | Type |
|--------|------|
| id | INTEGER PK |
| sort | TEXT |
| type | TEXT |
| description | TEXT |
| details | TEXT |
| cost | REAL |
| hours | INTEGER |
| manufacturer | TEXT |
| manuf_part_num | TEXT |
| dated | TEXT |
| revision_details | TEXT |
| stock_num | TEXT |

**391 rows** from `Stock.xlsx`

### clients, quote_num, status (from ClientDetails.mdb)

See Excel exports: `Clients.xlsx`, `QuoteNum.xlsx`, `Status.xlsx`

## Seed data

```powershell
cd backend
..\.venv\Scripts\python seed_db.py
```

Source directory (default): `../Old Program/Database doco/`

Override with `SEED_DATA_DIR` in `.env`.

## Migrations

Not yet implemented. Stage 2 will add Alembic when moving to PostgreSQL.
