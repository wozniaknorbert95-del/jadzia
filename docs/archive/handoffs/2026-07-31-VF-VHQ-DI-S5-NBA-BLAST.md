---
status: "[BLAST]"
title: "VF-VHQ-DI-S5-NBA — ranked Director next action"
updated: "2026-07-31"
gate: "VF-VHQ-DI-S5-NBA"
scorecard: "docs/ops/VHQ-DECISION-INSTRUMENT-SCORECARD.md"
dim: "S5"
cache_target: "vhq-w63a"
research: "docs/handoffs/2026-07-31-VF-VHQ-DECISION-INSTRUMENT-RESEARCH.md"
---

# BLAST — VF-VHQ-DI-S5-NBA

## Intent (1-1-1)

Exactly **one** primary “Director: do this now” card on MC L1, ranked by deterministic  
`money_proxy × p_close × urgency + risk − uncertainty` (no ML). Secondary priorities remain below. Honest fields; no fake €.

## Binary DoD

| # | DoD |
|---|-----|
| S5.1 | Exactly 1 primary Director NBA card (others secondary) |
| S5.2 | Deterministic score (formula above) |
| S5.3 | why-now · evidence_ts · owner · one CTA · cost_of_inaction · approval_class L1/L2 |
| S5.4 | Cold-open dogfood ≤30s (after GO DEPLOY) |
| S5.5 | Unit tests rank eligibility + order |

## Scope

| Path | Change |
|------|--------|
| `agent/commander/nba.py` | NEW — score + select + enrich |
| `agent/commander/queue.py` | `build_director_brief` / ranked priorities |
| `api/routes/commander.py` | `priorities/today` → `{nba, priorities}` |
| `commander-ui/*` | NBA mount + render · cache `vhq-w63a` |
| `tests/unit/test_commander_nba.py` | NEW |
| docs / todo | BLAST → PRECLOSE |

## STOP

No fake money KPI · no Order LIVE · no MKT · no 3D · no S6 money narrative · deploy only GO DEPLOY  
Preserve EV-W2-010 · INFO/stubs never NBA

## Validate

```bash
pytest tests/unit/test_commander_nba.py tests/unit/test_commander_queue.py tests/unit/test_commander_escalation.py -q
```
