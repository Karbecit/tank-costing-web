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
- [x] Costing UI — Summary, Cones, Strakes tabs with Calculate and JSON save/load

## Planned

- [ ] Components picker from stock database
- [ ] Components picker
- [ ] Labour and GST totals
- [ ] `.jma` full import/export
- [ ] PDF reports (7 report types)
- [ ] Dip chart
- [ ] Cone cutout calculator (DrawingOffice)
- [ ] User authentication (editor / read-only)
- [ ] Staging deployment
- [ ] Production deployment
