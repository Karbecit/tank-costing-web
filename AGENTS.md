# AGENTS.md — AI development rules

## Role

KarBec uses Cursor as the primary AI software engineer. The human is Product Owner.

## Before major changes

- Explain intent, alternatives, and risks
- Ask approval before breaking database schema changes
- Implement one stage at a time

## Code standards

- Production-quality, readable Python and JavaScript
- Follow existing patterns in this repo
- Keep modules small
- Avoid unnecessary dependencies
- Update documentation when features are completed

## Naming

- Python: `snake_case` for functions/variables, `PascalCase` for classes
- API routes: `/api/` prefix, plural nouns
- Database: `snake_case` columns

## Testing

- Add pytest tests for calculation logic and API endpoints
- CI must pass before merge to `main`

## Database

- Never commit `data/tankcosting.db`
- Document schema changes in `DATABASE.md`
- Use migrations (Alembic) once PostgreSQL is introduced

## Documentation

Keep these files current with the implementation:

- README.md, PROJECT.md, ARCHITECTURE.md, DATABASE.md, API.md, FEATURES.md, TODO.md, DECISIONS.md

## Legacy reference

VB6 source and scope docs are in `../Old Program/` — read before porting business logic.

## Communication

After completing work: summarise changes, explain how to run/test, suggest next step.
