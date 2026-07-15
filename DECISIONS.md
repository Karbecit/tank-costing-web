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

## ADR-006: Authentication and roles

**Date:** 2026-07-15  
**Status:** Accepted

- Session-based or JWT auth via FastAPI; **HTTPS required** in production (subdomain).
- Roles: **admin** (user/settings/SMTP management), **editor** (create/edit costings), **read-only** (view quotes and reports).
- Passwords hashed (bcrypt/argon2); no plaintext in DB or Git.
- **MFA policy:**
  - **Admin:** MFA required on **every** login (no trusted-device bypass).
  - **Editor / read-only:** MFA on **first login per device/browser**; user may mark device as **trusted** to skip MFA on subsequent logins from that device until trust is revoked or expires.
- Trusted device: secure HTTP-only cookie + server-side record; configurable trust duration (e.g. 30–90 days).

## ADR-007: SMTP and secrets

**Date:** 2026-07-15  
**Status:** Accepted (scope); customer email TBD

- SMTP host, port, credentials, and from-address configured in **admin settings**, stored outside Git (cPanel env or file outside web root).
- **Confirmed uses:** user invite, password reset, MFA codes.
- **Customer quote email:** requirements **not yet defined** — defer until Product Owner confirms.
- Admin UI includes **Test SMTP** before save.

## ADR-008: Customer data model

**Date:** 2026-07-15  
**Status:** Accepted

- **Do not migrate** legacy ClientDetails.mdb / old Excel client export as authoritative data — database is outdated.
- Start with a **fresh customer table**; add clients and quotes **as needed** through the UI.
- Existing seeded `clients` / `quote_num` rows may be removed or kept as dev samples only; not required for production cutover.
- Costings reference `client_id` and optional quote metadata when customer module is built.

## ADR-009: Hosting — JMA shared server (cPanel)

**Date:** 2026-07-15  
**Status:** Accepted (details TBC)

- **Host:** JMA web server via wholesaler **shared hosting** with **cPanel**.
- **URL (proposed):** `https://tankcalc.jmagroup.com.au` — subdomain and DNS **to be confirmed**.
- **Implications for stack:**
  - Confirm cPanel **Python application** support (Passenger / Setup Python App) for FastAPI, or whether a small **VPS-style** plan is needed for uvicorn.
  - Static frontend: build Vite to `dist/` and serve via subdomain document root or reverse proxy.
  - API on same subdomain (`/api`) or internal proxy from Apache/nginx in cPanel.
  - TLS: cPanel AutoSSL / Let's Encrypt on subdomain.
  - Secrets: cPanel environment variables or `.env` **outside** `public_html`; never in Git.
- **CI/CD:** GitHub Actions runs tests on push; deploy may be **manual upload**, **git pull on server**, or **cPanel Git Version Control** until a fuller pipeline is defined.
- **Database:** SQLite may suffice initially on shared hosting if single-server; PostgreSQL if host provides it — decide at deploy setup.
- **Python version (confirmed):** cPanel **Setup Python App** supports up to **3.13.13**; host **recommends 3.12.13** for production. Use **3.12.13** on the server unless a specific dependency requires otherwise; local dev on 3.13 is fine.
- Align CI to test on **3.12** (production target) and optionally 3.13.

## ADR-005: Separate repo from Old Program

**Date:** 2026-07-15  
**Status:** Accepted

New web app in `tank-costing-web/` repo. Legacy VB6 material stays in sibling folder, not committed to this repo.
