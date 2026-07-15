from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .database import get_connection, init_db
from .routers import calc, costings, customers


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Tank Costing API",
    version="0.1.0",
    description="KarBec redevelopment of JMA Tank Costing",
    lifespan=lifespan,
)

app.include_router(calc.router)
app.include_router(customers.router)
app.include_router(costings.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "Tank Costing", "version": "0.1.0"}


@app.get("/api/stats")
def stats():
    tables = ["rates", "stock", "clients", "quote_num", "status", "customers", "costings"]
    with get_connection() as conn:
        counts = {
            table: conn.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"]
            for table in tables
        }
    return counts


@app.get("/api/rates")
def list_rates(limit: int = 50, offset: int = 0, grade: str | None = None):
    query = "SELECT * FROM rates"
    params: list = []
    if grade:
        query += " WHERE grade = ?"
        params.append(grade.strip())
    query += " ORDER BY grade, thickness, width LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


@app.get("/api/stock")
def list_stock(limit: int = 50, offset: int = 0, item_type: str | None = None):
    query = "SELECT * FROM stock"
    params: list = []
    if item_type:
        query += " WHERE type LIKE ?"
        params.append(f"%{item_type.strip()}%")
    query += " ORDER BY sort, type, description LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


@app.get("/api/clients")
def list_clients(limit: int = 50, offset: int = 0):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM clients ORDER BY company_name LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
    return [dict(r) for r in rows]


@app.get("/api/quotes")
def list_quotes(limit: int = 50, offset: int = 0):
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT q.*, c.company_name, s.status AS status_name
            FROM quote_num q
            LEFT JOIN clients c ON c.client_id = q.client_id
            LEFT JOIN status s ON s.stat_id = q.stat_id
            ORDER BY q.id
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()
    return [dict(r) for r in rows]


@app.get("/api/clients/{client_id}")
def get_client(client_id: int):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM clients WHERE client_id = ?", (client_id,)
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Client not found")
    return dict(row)
