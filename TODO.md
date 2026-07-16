# TODO

## Stage 2 — Calculation engine

- [x] Port `Cones.bas` logic to Python with unit tests
- [x] Port `Strakes.bas` and `Summary.bas`
- [x] Parse sample `.jma` files for cone/strake/summary validation

## Stage 3 — Costing UI

- [x] Summary page form
- [x] Cones and Strakes screens
- [x] Save/load costing as JSON
- [x] Wire components picker from stock DB
- [x] Link costing to customer / quote record
- [x] Save/load costing to server (SQLite)

## Stage 4 — Customer details

- [x] Fresh customer CRUD (no legacy ClientDetails migration)
- [x] Company name via UI (+ New customer on Summary)
- [x] Full customer form (contact, addresses, notes)
- [x] Optional quote number / job reference on costing
- [x] Customer search on Summary screen (searchable combobox)
- [x] Attach customer to saved costing

## Stage 5 — Users, security & admin

- [x] User accounts (login, password policy, session/JWT)
- [x] Roles: admin, editor (quote), read-only
- [x] MFA: admin every login; users MFA on first login per device + trusted device option
- [x] Admin portal — user management (create, disable, reset password, role change)
- [x] Admin settings (SMTP and app config — not in Git)
- [x] Audit log for admin actions (recommended)
- [x] Account tab — change password, MFA setup/disable

## Stage 6 — Email (SMTP)

- [x] SMTP settings in admin (host, port, TLS, from address)
- [x] Email templates: new user invite, password reset, test send
- [x] Test send from admin UI
- [x] Send invite email on user create (optional checkbox)
- [x] Customer quote email (PDF attachment via **Email quote** button)

## Stage 7 — Reports & deployment

- [x] PDF report generation (quote download)
- [x] Dip chart (single-tank; calculate first)
- [ ] Cone cutout calculator (DrawingOffice) — **deferred** (separate legacy VB6 tool, not in repo)
- [x] `.jma` import (legacy VB6 files)
- [x] `.jma` export (core costing data + empty tail for legacy compatibility)
- [x] Persist costings in database
- [x] Deploy scripts and cPanel guide (`scripts/build-production.ps1`, `deploy/`, `DEPLOYMENT.md`)
- [x] SQLite on server (default; PostgreSQL optional later)
- [x] GitHub Actions CI (lint, pytest, frontend build)

## Go-live (manual — Paul / JMA)

- [ ] Confirm subdomain DNS → server
- [ ] cPanel: create subdomain, SSL, Setup Python App
- [ ] Upload build, set env vars, smoke test production
- [ ] Change default admin password; configure SMTP
