# API

Base URL (local): `http://127.0.0.1:8080`

Interactive docs: `http://127.0.0.1:8080/docs`

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
