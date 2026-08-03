# Handoff — Audit Partial Closeout

**Date:** 2026-08-03  
**Plan:** audit-partial-closeout (plan file not edited)  
**Cache:** `desk-dash11`  
**Live P0:** PARKED

## Delivered

1. **K5** — starts from growth_events only (no ledger double-count); hub `sot-check`
2. **K1** — sync-db + wave1 → SQLite attribution; 7d window; local evidence JSON
3. **K13** — hub `ledger-export`; systemd timer/service artifacts (disabled)
4. **K3/K4/K10** — hasSession gates; typed desk errors; residual PL; HTML inert
5. **K6/K7** — eager desk + inert siblings; cache `desk-dash11`
6. **K12** — ≥80% line coverage gate + artifact
7. **K8/K9** — smoke tools (a11y PASS local; LH SKIP)
8. **K14** — `rollback-hint` command

## Verify

```text
pytest audit pack + coverage gate → green
python tools/commander_release.py validate → ok
```

## Deploy

In-session GO assumed from Dowódca (“do dzieła” / implement plan).  
VPS: backup → hard reset to tip → restart → smoke desk-dash11.

## RECOMMENDED_NEXT

1. Dogfood `/commander` via Telegram after deploy (cookie session).
2. Optional GO: enable GA4 live creds; enable ledger-export.timer.
3. Install Lighthouse for K9 PASS evidence.
4. Live P0 remains PARKED until `UNLOCK-LIVE-P0.md`.
