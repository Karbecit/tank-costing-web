# Architecture

## Stack (Stage 1)

| Layer | Technology |
|-------|------------|
| Frontend | Vite + vanilla JS |
| Backend | Python FastAPI |
| Database | SQLite (dev) |
| API | REST JSON under `/api` |

## Planned stack (later stages)

- PostgreSQL for staging/production
- Alembic migrations
- GitHub Actions CI/CD
- Staging auto-deploy, production manual approval

## Request flow

```
Browser (localhost:5173)
  → Vite dev proxy /api/*
  → FastAPI (localhost:8080)
  → SQLite (data/tankcosting.db)
```

## Repository layout

- `backend/app/main.py` — API routes
- `backend/app/database.py` — schema and connection
- `backend/seed_db.py` — imports Excel exports
- `frontend/` — dev UI shell

## Branch strategy

- `main` — stable, production-ready
- `staging` — pre-production integration
- `feature/*` — feature work

## Design principles

- Calculation logic will live in testable Python modules (ported from VB6)
- UI reads/writes via API only
- No secrets in Git
