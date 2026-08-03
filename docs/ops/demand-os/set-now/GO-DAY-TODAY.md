---
title: "GO DAY — Marketing HITL (post 5f SEAL)"
date: "2026-08-03"
status: "awaiting GO MARKETING HITL"
master_todo: "docs/ops/demand-os/MASTER-TODO-4.md"
---

# GO DAY — Marketing HITL

**5f SEALED · go_day_ready 100%.** Marketing unpark tylko przez Founder GO.

| Reguła | Wartość |
|--------|---------|
| priority | `4-GO-01` GO MARKETING HITL |
| publish live | **STOP** until GO + VPS env |
| Ads | **PARK cash** |
| VPS kod | STOP · env-only po GO |
| checklist | [`GO-MARKETING-HITL-CHECKLIST.md`](../GO-MARKETING-HITL-CHECKLIST.md) |

## Agent verify (prep done)

```bash
python -c "from agent.demand_os.week_ritual import go_day_ready; print(go_day_ready()['score'])"
python -m pytest tests/test_demand_os_marketing_mode.py -q
```

## Po GO

1. VPS `DEMAND_OS_MARKETING_HITL=GO` · restart
2. TT HITL `tt_w32_install_01`
3. FB hunt · ledger

Sprint: [`ORGANIC-AGENCY-SPRINT-14D.md`](../ORGANIC-AGENCY-SPRINT-14D.md)
