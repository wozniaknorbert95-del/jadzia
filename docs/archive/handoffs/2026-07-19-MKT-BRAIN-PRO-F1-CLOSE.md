---
status: "[ACTIVE]"
title: "MKT-BRAIN-PRO F1 — Decision Engine + Shadow CLOSE"
gate: "MKT-BRAIN-PRO-F1"
updated: "2026-07-19"
result: "PASS"
tip: "9314ddc"
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
| pytest `test_mb_f1.py` | **7/7 PASS** |

## VPS evidence

| Check | Result |
|-------|--------|
| Tip | `9314ddc` |
| Backup | `jadzia-pre-mkt-brain-f1-20260719-145011.db` |
| Brain cycle | `ok=true records=1 telegram_sent=1` |
| Shadow API | LIVE · `HEU_ATTRIBUTION_LOW` hold shadow |
| Tables | shadow / hypotheses / brain_events |

## Also fixed this session (agent, not human)

| Item | Evidence |
|------|----------|
| GA4 SA missing on VPS | Restored from backup → `/opt/jadzia/secrets/` |
| GA4 re-ingest | steps_ok=6 · freshness ok |
| Telegram admin | fallback `ALLOWED_TELEGRAM_USERS` → `telegram_sent=1` |

## Human-only remaining (cannot automate)

| Item | Why |
|------|-----|
| Meta Events Manager InitiateCheckout/Purchase | Meta UI — no Ads API create |
| Shadow accuracy ≥70% over 14d | Human judgment before `MB_MODE=propose` |

## Env (VPS)

```
MB_MODE=shadow
MARKETING_BRAIN_INTERVAL_SECONDS=3600
MARKETING_DTL_INGEST_INTERVAL_SECONDS=3600
```
