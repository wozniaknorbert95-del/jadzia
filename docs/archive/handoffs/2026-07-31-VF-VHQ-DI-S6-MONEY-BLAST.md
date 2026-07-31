---
status: "[BLAST]"
title: "VF-VHQ-DI-S6-MONEY — honest money/risk narrative"
updated: "2026-07-31"
gate: "VF-VHQ-DI-S6-MONEY"
scorecard: "docs/ops/VHQ-DECISION-INSTRUMENT-SCORECARD.md"
dim: "S6"
cache_target: "vhq-w64a"
---

# BLAST — VF-VHQ-DI-S6-MONEY

## Intent (1-1-1)

MC L1 **money/risk narrative** from real lead/queue/freshness signals — or honest `insufficient_data` + one CTA.  
**No vanity €**, no green revenue totals, Order Desk stays **PARKED · EV-W2-010**.

## Binary DoD

| # | DoD |
|---|-----|
| S6.1 | Q1 from real Wizard/lead signals OR `insufficient_data` + one verify CTA |
| S6.2 | No vanity totals; no fake € green |
| S6.3 | Top risk blocker + owner when present |
| S6.4 | Prod dogfood + event IDs |

## Scope

| Path | Change |
|------|--------|
| `agent/commander/money_narrative.py` | NEW builder |
| `api/routes/commander.py` | `GET …/money-risk` |
| `tests/unit/test_commander_money_narrative.py` | NEW |
| `commander-ui/*` | `#vhq-money-risk` above NBA · cache `vhq-w64a` |

## STOP

No Order LIVE · no Mollie · no fake purchase_revenue on L1 · no MKT · no S7 unpark · deploy only GO DEPLOY

## Validate

```bash
pytest tests/unit/test_commander_money_narrative.py tests/unit/test_commander_nba.py tests/unit/test_commander_queue.py -q
```
