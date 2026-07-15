# Architecture Decisions

## ADR-001: SQLite for local development

**Date:** 2026-07-15  
**Status:** Accepted

Use SQLite locally for zero-config setup. PostgreSQL for staging/production in a later stage.

## ADR-002: FastAPI backend

**Date:** 2026-07-15  
**Status:** Accepted

Python FastAPI chosen for rapid development, good test support, and straightforward porting of VB6 calculation modules.

## ADR-003: Vite + vanilla JS for Stage 1 UI

**Date:** 2026-07-15  
**Status:** Accepted

Minimal frontend to verify API. React or similar can be introduced in Stage 3 when UI complexity grows.

## ADR-004: Seed from Excel exports

**Date:** 2026-07-15  
**Status:** Accepted

Legacy Access databases were replicated and incompatible with modern Access. Excel exports in `Database doco/` are the migration source.

## ADR-005: Separate repo from Old Program

**Date:** 2026-07-15  
**Status:** Accepted

New web app in `tank-costing-web/` repo. Legacy VB6 material stays in sibling folder, not committed to this repo.
