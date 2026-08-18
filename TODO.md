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



## Stage 8 — UI parity with v9 (see `UI_PARITY.md`)

Reference: `C:\Projects\Tank Costing\App screen shots.docx` (v9; 17 screenshots, *Ladbroke Grove Wines 35kl…*). Web side: `C:\Projects\Tank Costing\Website pages.docx` (Summary, Cones, Strakes). Sample `.jma` for QA: `C:\Projects\Tank Costing\Ladbroke Grove Wines 35kl storage tank 3050diam 4800wall 316 stst 14-7-09.jma` (full import OK).

### High priority

- [ ] Gross profit calculation + display (9.0 formula in `Instal_6_2_1\Summary.bas`)
- [ ] Summary dashboard: steel breakdown, labour grid, add-ons, multi-tank panel
- [ ] Add-on cost fields (`single_add_on` / `multi_add_on`) on Summary
- [ ] Select Coil picker + inline calc fields on Cones/Strakes
- [ ] Cone type toggles (Conical/Offset/Slope) with height↔angle coupling — **partial** (type dropdown + conditional fields; no auto coupling)
- [x] Volume/height treatment dropdown per cone and strake row
- [ ] Volumes & Heights footer on Cones/Strakes tabs
- [ ] Components dual-grid (stock browse + tank rows with hours/orientation)
- [x] Fix v9 `.jma` summary import for Ladbroke Grove sample (non-numeric early summary slots)

### Medium priority

- [ ] Qty Coil Used report
- [ ] Multi Floor Sheets / Additional Coil (Cones & Floors menu)
- [ ] Combo Tank volume modal
- [ ] Dip chart Excel/text export
- [ ] Change Diameter tool
- [ ] Pre-Set Values / default markups screen
- [ ] Costing metadata fields (rep, originator, status, change log)
- [ ] Report preview suite (Volume & Height, Coil Steel, Components, Labour) — old doc only
- [ ] Temperature-corrected volumes (@24°C / @4°C) on Summary

### Low priority

- [ ] Saved/unsaved indicator, last-saved audit line
- [ ] Non-stock components text area
- [ ] Cone intermediate rows / sand buildup / skirt UI



## Go-live (manual — Paul / JMA)




- [ ] Confirm subdomain DNS → server

- [ ] cPanel: create subdomain, SSL, Setup Python App

- [ ] Upload build, set env vars, smoke test production

- [ ] Change default admin password; configure SMTP

