# API

Base URL (local): `http://127.0.0.1:8080`

Interactive docs: `http://127.0.0.1:8080/docs`

## Endpoints

### GET /api/health

Health check.

```json
{ "status": "ok", "app": "Tank Costing", "version": "0.2.0" }
```

## Authentication

All endpoints except `/api/health` and `/api/auth/login` require a Bearer token.

### POST /api/auth/login

```json
{ "email": "admin@local", "password": "ChangeMe123!" }
```

Returns `access_token` and user profile, or `mfa_required` + `mfa_token` when MFA is enabled. Use header: `Authorization: Bearer <token>`.

Optional cookie `tc_trust` skips MFA for non-admin users on trusted devices (90 days).

### POST /api/auth/mfa/verify

Complete login after MFA challenge. Body: `mfa_token`, `code`, optional `trust_device` (non-admin only).

### POST /api/auth/change-password

Body: `current_password`, `new_password` (min 10 chars, upper, lower, digit).

### POST /api/auth/mfa/setup

Start MFA setup — returns `secret` and `otpauth_uri` for authenticator app.

### POST /api/auth/mfa/confirm

Body: `code` — enable MFA after setup.

### POST /api/auth/mfa/disable

Body: `code` — disable MFA.

### GET /api/auth/me

Current user profile (includes `mfa_enabled`).

### GET /api/admin/users

Admin only — list users.

### GET /api/admin/audit

Admin only — recent audit log entries. Query param: `limit` (default 100).

### POST /api/admin/users
Admin only — create user (`email`, `display_name`, `password`, `role`: admin|editor|viewer).

Roles: **viewer** (read-only), **editor** (create/edit costings), **admin** (user management).

### POST /api/admin/users/{user_id}/send-invite

Admin only — email account details. Body: `{ "password": "..." }` (password to include in email).

### GET /api/admin/settings/smtp

Admin only — SMTP settings (password masked).

### PUT /api/admin/settings/smtp

Admin only — save SMTP settings.

### POST /api/admin/settings/smtp/test

Admin only — send test email. Body: `{ "to": "user@example.com" }`.

### POST /api/jma/parse

Upload a `.jma` file (multipart `file`) — returns parsed title, quote ref, and payload preview.

### POST /api/jma/import

Editor+ — upload `.jma` file, create costing record (201).

### GET /api/costings/{costing_id}/export.jma

Download legacy `.jma` file for a saved costing.

### POST /api/costings/{costing_id}/email-quote

Email PDF quote to customer (or `to` in body). Requires SMTP configured.

### POST /api/calc/dip-chart

Single-tank dip chart. Body: `payload`, optional `increment_mm` (default 10).

### GET /api/stats

Row counts per table.

### GET /api/rates

Query params: `limit`, `offset`, `grade`

### GET /api/stock

Query params: `limit`, `offset`, `item_type`

### GET /api/clients

Query params: `limit`, `offset`

### GET /api/clients/{client_id}

Single client record.

### GET /api/quotes

Query params: `limit`, `offset` — includes joined company and status names.

### POST /api/calc/cone

Calculate cone geometry, volume, and steel pricing from input dimensions.

Request body:

```json
{
  "cone": {
    "conic_select": 1,
    "angle_select": true,
    "diam_large": 1200,
    "diam_small": 450,
    "angle": 10,
    "knuckle_rad": 30,
    "waste": 300,
    "thick": 2,
    "width": 1500,
    "weight_cucm": 8166,
    "price_kg": 5.8
  },
  "tank_diam": 1200
}
```

Response includes computed `height`, `volume`, `length`, `surface_area`, `weight`, `steel_price`, etc.

Cone types: `conic_select=1` (conical), `offset_select=1` (offset), `slope_select=1` (sloped floor).

### POST /api/calc/strake

Calculate strake volume and steel from input dimensions.

### POST /api/calc/costing

Calculate all cones, strakes, and summary totals in one request. Body includes `cones[]`, `strakes[]`, and `summary` (diameter, expansion chamber, markup, GST, etc.).

### GET /api/customers

Query params: `limit`, `offset`, `q` (search company, contact, email)

### POST /api/customers

Create a customer. Body: `company_name` (required), optional `contact_name`, `email`, `phone`, addresses, etc.

### GET /api/customers/{customer_id}

Single customer record.

### PUT /api/customers/{customer_id}

Update customer fields.

### DELETE /api/customers/{customer_id}

Delete customer (204).

### GET /api/costings

List saved costings (most recently updated first). Query params: `limit`, `offset`.

### POST /api/costings

Save a new costing. Body:

```json
{
  "title": "Pettavel 5KL",
  "quote_ref": "Q-2026-042",
  "customer_id": 1,
  "payload": { "version": 1, "summary": {}, "cones": [], "strakes": [] }
}
```

### GET /api/costings/{costing_id}

Load a saved costing (includes parsed `payload` JSON).

### PUT /api/costings/{costing_id}

Update an existing costing.

### DELETE /api/costings/{costing_id}

Delete a saved costing (204).
