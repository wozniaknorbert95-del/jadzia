# HANDOFF — DEMAND MARKETING 4 PREP CLOSE

**Date:** 2026-08-03  
**Gate:** `DEMAND-OS-MARKETING-4-00` **ACTIVE (prep done)**  
**Prerequisite:** Etap 5f SEALED · Hard DoD 15/15  
**Status:** **PREP CLOSE** — awaiting Founder `GO MARKETING HITL`

## Werdykt

Etap 4 gotowy do unpark. Maszyna + UI + checklist. **Live publish nadal BLOCKED** do GO.

## Deliverables

| ID | Item | Status |
|----|------|--------|
| 4-PREP-01 | `agent/demand_os/marketing_mode.py` — env `DEMAND_OS_MARKETING_HITL=GO` | ✅ |
| 4-PREP-02 | `MASTER-TODO-4.md` + `GO-MARKETING-HITL-CHECKLIST.md` | ✅ |
| 4-PREP-03 | go_day_ready **100%** · pytest marketing_mode | ✅ |
| 4-PREP-04 | ICP-BRIEF-W1 → sanitized set-now | ✅ |

## Verify

```text
go_day_ready score: 100.0 · marketing_hitl_gate: BLOCKED (default)
pytest tests/test_demand_os_marketing_mode.py → 3/3 PASS
pytest desk contract + tool100 + api desk → 29/29 PASS
```

## GO ceremony (human — 4-GO-01)

1. Wpis **`GO MARKETING HITL`** + data w handoff
2. VPS: `DEMAND_OS_MARKETING_HITL=GO` · restart jadzia
3. Agent verify: `marketing_hitl_gate: READY` prod
4. First actions: TT `tt_w32_install_01` · FB hunt · ledger

Checklist: [`GO-MARKETING-HITL-CHECKLIST.md`](../ops/demand-os/GO-MARKETING-HITL-CHECKLIST.md)

## STOP

- Live publish bez GO
- Ads / € spend
- VPS deploy kodu bez GO (env-only po GO)

## Rollback GO

Usuń `DEMAND_OS_MARKETING_HITL` z `.env` · restart → gate BLOCKED.
