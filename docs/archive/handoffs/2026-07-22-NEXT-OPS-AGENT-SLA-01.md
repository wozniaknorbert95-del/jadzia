# Next — OPS-AGENT-SLA-01 (post freshness LIVE)

**Date:** 2026-07-22  
**Context tip:** `058d568` · cache `mkt-dash07` · freshness clocks LIVE  
**Prior:** `2026-07-22-OPS-FRESHNESS-01-DEPLOY-CLOSE.md`

## Why this (expert)

Ops rail after freshness fix: **Freshness ok · GA4 ok**, summary still  
`Ops: UWAGA — SLA bad 5`. That is the last loud trust signal on Start.  
FB token stays **deferred until dashboard complete** (Dowódca).

## TASK

```text
TASK_ID: OPS-AGENT-SLA-01
REPO: jadzia-core
CLASS: BugFix / HotFix
```

**Misja:** Zdiagnozuj i napraw (lub świadomie parkuj) `sla_ok=false` na ~5 agentach w `/api/v1/agents` + chip SLA — bez fake PASS, bez deploy bez GO.

**DoD:**
- [x] RCA: które agenty, jaki clock (`last_run` / `next_expected_run` / interval)
- [x] Fix honesty (SLA ok gdy deserved) **lub** park `ready_for_human` z owner
- [x] Unit/contract jeśli zmieniasz SLA logic
- [ ] Dogfood LIVE Start po deploy — **blocked on GO** (`NEXT-OPS-AGENT-SLA-01-DEPLOY`)

**CLOSE:** `docs/handoffs/2026-07-22-OPS-AGENT-SLA-01-CLOSE.md`

**Hard STOP:** no FB token work · no secrets · no VPS bez GO · no execute UI

## Deferred

`OPS-FB-TOKEN-01` — po ukończeniu dashboardu.
`CMD-DASH-L1L2` — Low polish (shadow group-by, nav truncate) — non-blocking.
