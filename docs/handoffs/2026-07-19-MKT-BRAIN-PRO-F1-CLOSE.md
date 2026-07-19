---
status: "[ACTIVE]"
title: "MKT-BRAIN-PRO F1 — Decision Engine + Shadow CLOSE"
gate: "MKT-BRAIN-PRO-F1"
updated: "2026-07-19"
result: "PASS (pending VPS tip after deploy)"
---

# MKT-BRAIN-PRO F1 — CLOSE

## Deliverables

| Item | Status |
|------|--------|
| `heuristics.py` HEU_DATA_QUALITY / PROFIT_WATCHDOG / ORGANIC_WINNER / ATTRIBUTION | DONE |
| `decision_engine.py` + shadow persist | DONE |
| `marketing_shadow_log` + `marketing_hypotheses` + `brain_events` | DONE |
| Telegram `mb_approve/deny/details` (shadow, no side-effects) | DONE |
| Worker `MARKETING_BRAIN_INTERVAL_SECONDS` | DONE |
| Heartbeat agent `marketing_brain` | DONE |
| pytest `test_mb_f1.py` | DONE |

## Also fixed this session (agent, not human)

| Item | Evidence |
|------|----------|
| GA4 SA missing on VPS | Restored from `/root/jadzia-backup-20260630-062926/secrets/` → `/opt/jadzia/secrets/` |
| Property IDs | `528764186` / `528785553` from INT-009 proof |
| Re-ingest | steps_ok=6 steps_error=0 · ga4 freshness ok |

## Human-only remaining (cannot automate)

| Item | Why |
|------|-----|
| Meta Events Manager InitiateCheckout/Purchase click-verify | Meta UI / Ads Manager — no API create (PARK) |
| Shadow accuracy ≥70% Dowódca review over 14d | Human judgment before `MB_MODE=propose` |

## Env (VPS)

```
MB_MODE=shadow
MARKETING_BRAIN_INTERVAL_SECONDS=3600
MARKETING_DTL_INGEST_INTERVAL_SECONDS=3600
```
