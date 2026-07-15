# Tank Costing Web

Web-based redevelopment of the JMA Tank Costing program (VB6 legacy).

## Quick start (local)

```powershell
cd "C:\Projects\Tank Costing\tank-costing-web"
.\scripts\setup.ps1
.\scripts\start.ps1
```

- **Frontend:** http://localhost:5173
- **API:** http://localhost:8000/api/health
- **API docs:** http://localhost:8000/docs

## Prerequisites

- Python 3.11+
- Node.js 20+
- Git
- Excel seed files in `../Old Program/Database doco/`

## Project structure

```
tank-costing-web/
  backend/          FastAPI API + SQLite
  frontend/         Vite dev UI
  data/             Local SQLite (gitignored, created by seed)
  scripts/          Setup and start helpers
  .github/          CI workflows
```

## Documentation

| File | Description |
|------|-------------|
| [PROJECT.md](PROJECT.md) | Business context |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Technical design |
| [DATABASE.md](DATABASE.md) | Schema and seed data |
| [API.md](API.md) | REST endpoints |
| [AGENTS.md](AGENTS.md) | AI development rules |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Deploy pipeline (future stages) |

## Switching computers

```powershell
git pull
.\scripts\setup.ps1
.\scripts\start.ps1
```

GitHub is the source of truth — do not rely on OneDrive for project files.
