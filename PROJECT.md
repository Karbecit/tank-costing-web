# Project — Tank Costing Web

## Client

JMA Engineering Pty Ltd (via KarBec redevelopment)

## Purpose

Replace the legacy VB6 Tank Costing desktop application with a modern web application for quoting stainless steel storage tanks.

## Legacy reference

Source material lives in `../Old Program/`:

- VB6 source (`Code/`)
- Scope documents (`Scope documents/`)
- Database exports (`Database doco/`)
- Sample costings (`.jma` files)

**Current stage**

**Stage 3 — Costing UI** (core tabs done; components & customer linking next)

## Roadmap (updated)

| Stage | Focus |
|-------|--------|
| 1–2 | ✅ Scaffold, DB seed, calculation engine |
| 3 | Costing UI, components picker, quote workflow |
| 4 | **Customer details** — contacts, addresses, quotes |
| 5 | **Users & security** — login, roles, admin portal, MFA |
| 6 | **Email** — SMTP settings, invites, MFA, customer quote send |
| 7 | Reports, `.jma` migration, DB persistence, **cPanel deploy** |

**Hosting (accepted):** Shared server with **cPanel**; subdomain e.g. `tankcalc.jmagroup.com.au` (TBC).

**Customers:** Fresh data in app — **no** migration of old ClientDetails.

**MFA:** Admin every login; users MFA once per device then optional trusted browser.

**Customer email:** TBC.

## Future stages (detail)

3. Components + customer on costing
4. Customer / quote management
5. User management, admin settings, MFA
6. SMTP and transactional email
7. PDF reports, dip chart, hosting
