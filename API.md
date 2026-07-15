# API

Base URL (local): `http://127.0.0.1:8000`

Interactive docs: `http://127.0.0.1:8000/docs`

## Endpoints

### GET /api/health

Health check.

```json
{ "status": "ok", "app": "Tank Costing", "version": "0.1.0" }
```

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
