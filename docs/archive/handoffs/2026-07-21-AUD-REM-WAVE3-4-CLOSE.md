# Handoff — AUD-REM Wave3–4 (WRITE / HEALTH / DB / PRIVACY / OPS / SOT)

**Date:** 2026-07-21  
**Status:** LOCAL PASS · PR pending · **NO VPS** (`standing_go_closeout=false`)  
**Base:** `master` @ `da46c49` (PR #9 merged)

## Closed this batch

| Task | Finding | Evidence |
|------|---------|----------|
| WRITE-01 | F-04 | Partial multi-file write → stop + rollback → `ROLLED_BACK`/`FAILED`; never `COMPLETED`. Fault-injection tests. Configurable `WP_HEALTH_CHECK_URL`/`SHOP_URL`. |
| HEALTH-01 | F-06 | `set_health_metrics(health_metrics)` on startup; forced-failure → `/worker/health` counters. Process-local (documented). |
| DB-01 | F-08 | `PRAGMA journal_mode=WAL`, `busy_timeout=30000`, connect `timeout=30`. Microbench + pragma tests. Single-process note in systemd + SLO runbook. |
| PRIVACY-01 | F-10 | `purge_expired_portal_qual_leads` on startup; minimized Telegram hot-lead payload; retention test. |
| OPS-01 | F-12 | [`docs/ops/SLO-DR-RUNBOOK.md`](../ops/SLO-DR-RUNBOOK.md); deploy DB upload defaults to **N**; systemd ProtectSystem/Home/Devices/RestrictAddressFamilies. |
| SOT-01 | F-13 | Hot handoffs ≤15; archive move; README + audit status refresh. |

## Widget session_id

Fixed in **flexgrafik-nl** `flexgrafik-child/assets/js/chat-widget.js`: adopt server-returned `session_id` into `sessionStorage` (no client-only mint for continuity).

## Not done here (HITL)

- VPS deploy / `AUD-REM-VPS-VERIFY-01` — see `2026-07-21-AUD-REM-VPS-READY.md`
- Restore drill evidence (human)
- Production scorecard PASS

## Tests

```text
uv run --locked python -m pytest tests/test_nodes_approval.py \
  tests/test_health_metrics_wiring.py tests/test_db_wal_and_retention.py -q
```
