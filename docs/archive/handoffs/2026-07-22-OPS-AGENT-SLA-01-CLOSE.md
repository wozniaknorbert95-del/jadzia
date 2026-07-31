# Handoff CLOSE — OPS-AGENT-SLA-01 (code ready · deploy HITL)

**Date:** 2026-07-22  
**Status:** **CODE READY → DEPLOY_READY** — see `2026-07-22-OPS-AGENT-SLA-01-DEPLOY-READY.md`  
**Cache bump:** `mkt-dash08`  
**Base tip LIVE:** `058d568` · runtime freshness `@c210578` · UI `mkt-dash07` until deploy  
**standing_go_closeout:** `false`

## RCA (LIVE evidence)

Dogfood Start `@mkt-dash07` (JWT session):

| Signal | Value |
|--------|-------|
| Summary | `Ops: UWAGA — freshness amber · SLA bad 5` |
| Chip SLA | `bad: 5` |
| Freshness | ga4/orders/leads **amber** (~2015s) · worker **ok** |

`GET /api/v1/agents` (LIVE):

| agent_id | last_run_at | sla_ok | Root cause |
|----------|-------------|--------|------------|
| marketing_brain | 2026-07-22T11:27:24Z | **true** | MB heartbeat OK |
| marketing | 2026-07-17T14:21:10Z | false | HITL publish clock, 5d stale — not auto SLA |
| analytics | null | false | no writer; pipeline = DTL ga4 |
| sales | null | false | no writer; pipeline = DTL leads |
| operations | null | false | no writer; pipeline = DTL orders |
| design | null | false | on-demand INSPIRE; no schedule |

**Root cause:** Start chip counted `!sla_ok` (null last_run → false alarm). Agenci tab already showed `n/a` for missing clocks — inconsistency.

## Fix (honesty, no fake PASS)

1. `agents_registry.py` — DTL fallback clocks for analytics/sales/operations; `sla_ok=null` for HITL marketing + on-demand design; expose `clock_source`
2. `commander-ui/app.js` — `slaBad` only when `sla_ok === false`; Agenci/map labels treat `null` as `n/a`
3. `escalation.py` / `queue.py` — silent-agent checks use `is False`
4. Cache `mkt-dash08`

**Projected post-deploy Start (from LIVE clocks):** SLA bad **0** (Freshness amber may still UWAGA — honest, separate rail).

## Tests

```text
pytest tests/unit/test_agents_sla_honesty.py tests/unit/test_agents_next_expected.py -q
→ 10 passed
```

## Hard STOP held

- No SSH / VPS deploy (no GO)
- No FB token / secrets
- No execute UI / no hot_lead Confirm

## LEFT / NEXT

| Item | Owner | When |
|------|-------|------|
| **Deploy OPS-AGENT-SLA-01** (`mkt-dash08`) | human GO → agent | **ready_for_human** |
| Post-deploy dogfood Start | agent | after GO |
| `OPS-FB-TOKEN-01` | human | after dashboard complete |
| `CMD-DASH-L1L2` | agent | non-blocking |

## Files

- `agent/commander/agents_registry.py`
- `agent/commander/escalation.py`
- `agent/commander/queue.py`
- `commander-ui/app.js`
- `commander-ui/index.html`
- `tests/unit/test_agents_sla_honesty.py`
- `deployment/_ops_agent_sla_rca.py`

## NEXT_COMMAND (after GO deploy)

```text
@vibe-init
TASK_ID: OPS-AGENT-SLA-01-DEPLOY
REPO: jadzia-core
GO: deploy tip with mkt-dash08 · dogfood Start SLA chip
SoT: docs/handoffs/2026-07-22-OPS-AGENT-SLA-01-CLOSE.md
```
