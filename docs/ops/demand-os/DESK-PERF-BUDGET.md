# K9 — Demand Desk performance budget

## Targets (throttled mobile)
- LCP < 2.5s
- CLS < 0.1
- INP < 200ms
- Lighthouse Performance ≥ 80

## CI hooks
- Cache bust must be present (`desk-dash*`)
- Non-desk views lazy/inert (K6)
- SW must not cache `/api/`

## Evidence
Attach 3 Lighthouse JSON runs under `docs/handoffs/evidence/` after deploy GO.
