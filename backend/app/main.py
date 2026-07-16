from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .auth.dependencies import CurrentUser, get_current_user
from .database import get_connection, init_db
from .routers import admin, auth, calc, costings, customers, jma

_user = Annotated[CurrentUser, Depends(get_current_user)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Tank Costing API",
    version="0.2.0",
    description="KarBec redevelopment of JMA Tank Costing",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(calc.router)
app.include_router(customers.router)
app.include_router(costings.router)
app.include_router(jma.router)

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
    return {"status": "ok", "app": "Tank Costing", "version": "0.2.0"}


@app.get("/api/stats")
def stats(_user: _user):
    tables = ["rates", "stock", "clients", "quote_num", "status", "customers", "costings", "users"]
    with get_connection() as conn:
        counts = {
            table: conn.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"]
            for table in tables
        }
    return counts


@app.get("/api/rates")
def list_rates(_user: _user, limit: int = 50, offset: int = 0, grade: str | None = None):
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
def list_stock(_user: _user, limit: int = 50, offset: int = 0, item_type: str | None = None):
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
def list_clients(_user: _user, limit: int = 50, offset: int = 0):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM clients ORDER BY company_name LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
    return [dict(r) for r in rows]


@app.get("/api/quotes")
def list_quotes(_user: _user, limit: int = 50, offset: int = 0):
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
def get_client(client_id: int, _user: _user):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM clients WHERE client_id = ?", (client_id,)
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Client not found")
    return dict(row)
