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
VPS tip **`c04d1b4`**: backup → hard reset → restart → smoke `desk-dash11` + `/health` ok.  
Evidence: `docs/handoffs/evidence/audit-k-2026-08-03/k14-deploy-smoke.md`.

**K2 prod:** SA file missing at configured path → fail-closed `unavailable` (`k2-ga4-status-prod.json`). `DEMAND_OS_GA4_LIVE` left off until real credentials file exists.

## RECOMMENDED_NEXT

1. Dogfood `/commander` via Telegram (cookie session) — tool residual only.
2. Optional GO: place GA4 SA file + enable live; enable ledger-export.timer.
3. Install Lighthouse for K9 PASS evidence.
4. Live P0 remains PARKED until `UNLOCK-LIVE-P0.md`.
