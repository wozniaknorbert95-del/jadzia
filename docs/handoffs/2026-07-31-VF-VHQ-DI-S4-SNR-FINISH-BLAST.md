---
status: "[BLAST]"
title: "VF-VHQ-DI-S4-SNR-FINISH — analytics_stale out of Decide-now"
updated: "2026-07-31"
gate: "VF-VHQ-DI-S4-SNR-FINISH"
scorecard: "docs/ops/VHQ-DECISION-INSTRUMENT-SCORECARD.md"
dim: "S4"
cache_target: "vhq-w63a (only if commander-ui changes; prefer API-only → keep vhq-w62a)"
baseline_tip: "6e357cc"
feature_snr_w1: "4c1ab56"
---

# BLAST — VF-VHQ-DI-S4-SNR-FINISH

## Intent (1-1-1)

Finish S4 Signal-to-noise: chronic `analytics_stale` / data-quality must **not** occupy Decide-now CRITICAL/ACTION primary rail. Keep honesty via queue INFO + Ops “data confidence degraded” (W1 already).

**Chosen path (safest):** demote `QUEUE_SEVERITY["analytics_stale"]` **ACTION → INFO**.  
`build_priorities_today` already merges only CRITICAL+ACTION → GA4 stale leaves Decide-now automatically; remains visible in queue hygiene/INFO lane. No fake green on Analytics room.

## Binary DoD (from scorecard)

| # | DoD | Status |
|---|-----|--------|
| S4.1 | Decide-now stub contamination = 0% | DONE (W1) — regression |
| S4.2 | Chronic freshness never sole Ops UWAGA | DONE (W1) — regression |
| S4.3 | `analytics_stale` not in Decide-now CRITICAL/ACTION | **THIS GATE** |
| S4.4 | Noise ratio non-actionable / Decide-now **&lt;10%** on prod dogfood | **THIS GATE** |
| S4.5 | pytest + prod JWT dogfood evidence | **THIS GATE** |

## Scope (allowlist)

| Path | Change |
|------|--------|
| `agent/commander/constants.py` | `analytics_stale` → `INFO` |
| `tests/unit/test_commander_queue.py` | failing→green: stale not in priorities; severity INFO |
| `docs/handoffs/*` · `todo.json` · scorecard row after evidence | CLOSE |
| `commander-ui/**` | **only if** badge/label needed for INFO analytics — prefer none |

## Out of scope

- S5 NBA / S6 money / S3 approvals / S7 Order / S8 composite
- TTL cleanup of CEO stubs
- Fake GA4 refresh / inventing analytics LIVE
- MKT · 3D · Ads · Mollie · Order Desk unpark

## STOP

- No fake KPI / greenwash `insufficient_data`
- Preserve EV-W2-010 Order PARKED
- No MKT staging
- Deploy only with in-session `GO DEPLOY`
- Do not mega-diff into S5

## Tests first

```text
1. With GA4 snapshot amber/red → queue has analytics_stale severity INFO
2. build_priorities_today() contains zero queue_type=analytics_stale
3. Existing ceo_stub / publish_failed tests still green
```

## Validate

```bash
pytest tests/unit/test_commander_queue.py tests/unit/test_commander_escalation.py -q
```

## Ship

`/post-coding` → push → **GO DEPLOY** → backup DB → pull → restart → health  
Dogfood: `?v=<cache>` · Decide-now titles · stub 0% · Ops confidence line · screenshot → bump scorecard S4→**5** → pop queue → active=`VF-VHQ-DI-S5-NBA`

## Evidence dir

`docs/handoffs/evidence-vhq-di-s4/`
