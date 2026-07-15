# Features

## Implemented (v0.1.0)

- [x] Project scaffold (FastAPI + Vite)
- [x] SQLite schema for rates, stock, clients, quotes, status
- [x] Seed from legacy Excel exports
- [x] REST API for reference data
- [x] Dev UI showing sample data
- [x] Health check endpoint
- [x] CI build and test on push
- [x] Cones calculation engine (conical, offset, slope)
- [x] Strakes and Summary totals calculation
- [x] `.jma` parser for cones, strakes, and summary fields
- [x] POST `/api/calc/cone`, `/api/calc/strake`, `/api/calc/costing`
- [x] Costing UI — Summary, Cones, Strakes, Components tabs with Calculate and JSON save/load
- [x] Server save/load costings with customer linking
- [x] Customer CRUD API (fresh records, no legacy migration)
- [x] Components picker from stock database

## Planned

### Costing workflow (Stage 3 remainder)
- [ ] Full customer form in UI (contact, addresses)
- [ ] Quote number / job reference on costing

### Customer details (Stage 4)
- [ ] Extended customer records in UI
- [ ] Customer search on Summary screen

### Users, security & admin (Stage 5)
- [ ] Login, roles (admin / editor / read-only)
- [ ] MFA: admin always; users trust device after first MFA per browser
- [ ] Admin portal — users and settings

### Email (Stage 6)
- [ ] Admin-configurable SMTP (invites, MFA, password reset)
- [ ] Customer quote email — deferred pending requirements

### Reports & platform (Stage 7)
- [ ] PDF reports, dip chart, DrawingOffice cutout
- [ ] Full `.jma` import/export
- [x] DB-persisted costings (SQLite)
- [ ] Production on JMA cPanel shared host (`tankcalc.jmagroup.com.au` TBC)
