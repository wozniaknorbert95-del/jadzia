---
status: "[SUPERSEDED-BY-CLOSE]"
title: "VF-VHQ-W5-OPERATIONS-BUS — local implement PRECLOSE"
updated: "2026-07-31"
gate: "VF-VHQ-W5-OPERATIONS-BUS"
founder_go_implement: true
cache: "vhq-w50a"
prod_baseline: "6375ab1 / vhq-w40c"
commit: false
deploy: false
pytest_ops_bus: "9/9 PASS"
verify_pass: true
close: "docs/handoffs/2026-07-31-VF-VHQ-W5-OPERATIONS-BUS-CLOSE.md"
dogfood: "docs/handoffs/2026-07-31-VF-VHQ-W5-OPERATIONS-BUS-FOUNDER-DOGFOOD.md"
---

# PRECLOSE — VF-VHQ-W5-OPERATIONS-BUS

## Verdict

**Local implement + deep verify READY FOR FOUNDER DOGFOOD / CLOSE.**  
Typed Operations Bus cash spine live in code: `lead_qualified` → `wizard_started` → `order_created` + approval hooks.  
Order Desk remains **PARKED · EV-W2-010**. No deploy without separate GO.

## Evidence matrix

| ID | Claim | Result |
|----|-------|--------|
| EV-W5-001 | `lead_qualified` from disposition `acked` + audit | PASS (`test_lead_disposition_acked_emits_lead_qualified`) |
| EV-W5-002 | `wizard_started` sales_cta + ingest beacon | PASS (`test_sales_cta_spawn_…` + ingest API) |
| EV-W5-003 | `order_created` WC first-insert only | PASS (`test_order_webhook_emits_order_created_once`) |
| EV-W5-004 | audit chain valid after bus emits | PASS (`test_ops_bus_l2_pending_and_l3_stop`) |
| EV-W5-005 | L2 pending; L3 STOP stored as L3 + approve forbidden | PASS |
| EV-W2-010 | Order Desk PARKED on all honesty surfaces | PASS (manifest unchanged LIVE) |

## Binary DoD

| ID | Result |
|----|--------|
| D1 schema + CHECKs | PASS |
| D2 lead_qualified disposition | PASS |
| D3 wizard_started CTA/beacon | PASS |
| D4 order_created insert-only | PASS |
| D5 audit chain | PASS |
| D6 L2/L3-L4 hooks | PASS |
| D7 EV-W2-010 | PASS |
| D8 GET JWT / flag off | PASS |
| D9 UI typed trail (vhq-w50a) | PASS (Founder dogfood) |
| D10 evidence + pytest | PASS 9/9 |

## Delivered surface

- `agent/ops_bus/` — catalog, emit, flags
- `agent/db.py` — `ops_bus_events` + helpers
- Hooks: disposition acked · sales_cta spawn · order first-insert
- API: `GET/POST .../ops-bus/*` (`api/routes/ops_bus.py`)
- UI: flow last-hop · wizard bus cards · order trail under PARKED · CTA beacon · cache `vhq-w50a`

## STOP still held

- No free-form chat bus · no silent L3/L4 · no Order LIVE · no MKT · no Ads/Mollie · no prod deploy

## Founder next

1. ~~Local dogfood~~ → **PASS** (`FOUNDER-DOGFOOD`)  
2. ~~CLOSE~~ → `2026-07-31-VF-VHQ-W5-OPERATIONS-BUS-CLOSE.md`  
3. COMMIT exclude `docs/ops/marketing/**`  
4. Separate `GO DEPLOY` (Zasada 11)

PRECLOSE_VERDICT: **SUPERSEDED BY CLOSE** (deploy GO separate)
