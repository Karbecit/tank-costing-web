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

**Stage 2 complete — Calculation engine**

- Cones, Strakes, and Summary totals ported from VB6
- Validated against legacy `.jma` sample files
- API endpoints: `/api/calc/cone`, `/api/calc/strake`, `/api/calc/costing`

## Future stages

1. ~~Port calculation engine~~ (done)
2. Costing workflow UI (Summary page first)
3. `.jma` file import
4. PDF reports
5. Staging deployment
6. Production deployment with manual approval
