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
- [ ] Full customer form (contact, addresses, notes)
- [ ] Optional quote number / job reference on costing
- [ ] Customer search on Summary screen
- [x] Attach customer to saved costing

## Stage 5 — Users, security & admin

- [ ] User accounts (login, password policy, session/JWT)
- [ ] Roles: admin, editor (quote), read-only
- [ ] MFA: admin every login; users MFA on first login per device + trusted device option
- [ ] Admin portal — user management (create, disable, reset password)
- [ ] Admin settings (SMTP and app config — not in Git)
- [ ] Audit log for admin actions (recommended)

## Stage 6 — Email (SMTP)

- [ ] SMTP settings in admin (host, port, TLS, from address)
- [ ] Email templates: new user invite, password reset, MFA code
- [ ] Test send from admin UI
- [ ] Customer quote email — **deferred** (requirements TBC)

## Stage 7 — Reports & deployment

- [ ] PDF report generation
- [ ] Dip chart
- [ ] Cone cutout calculator (DrawingOffice)
- [ ] Full `.jma` import/export
- [x] Persist costings in database
- [ ] Deploy to cPanel — `tankcalc.jmagroup.com.au` (subdomain TBC)
- [ ] PostgreSQL or SQLite on server (confirm with host)
- [ ] GitHub Actions CI; manual / cPanel deploy to production
