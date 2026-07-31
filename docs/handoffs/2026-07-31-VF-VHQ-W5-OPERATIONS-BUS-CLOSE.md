---
status: "[CLOSE]"
title: "VF-VHQ-W5-OPERATIONS-BUS — CLOSE"
updated: "2026-07-31"
gate: "VF-VHQ-W5-OPERATIONS-BUS"
cache: "vhq-w50a"
local_url: "http://127.0.0.1:8000/commander/?v=vhq-w50a"
pytest_ops_bus: "9/9 PASS"
commit: pending_allowlist
deploy: false
w5_closed: true
founder_verdict: "CLOSED after local JWT dogfood PASS"
dogfood: "docs/handoffs/2026-07-31-VF-VHQ-W5-OPERATIONS-BUS-FOUNDER-DOGFOOD.md"
evidence_dir: "docs/handoffs/evidence-vhq-w50-dogfood/"
prod_baseline: "6375ab1 / vhq-w40c"
standing_go_closeout: false
next: "COMMIT W5 allowlist (no MKT) → exact GO DEPLOY → jadzia-test → audit → jadzia-deploy → prod dogfood → stamp"
---

# VF-VHQ-W5-OPERATIONS-BUS — CLOSE

**Status: CLOSED** after local JWT dogfood PASS (`vhq-w50a`).  
Deploy remains **blocked** until exact `GO DEPLOY` / `GO jadzia-deploy` (Zasada 11 · `standing_go_closeout=false`).

## Final DoD

| ID | Claim | Result |
|----|-------|--------|
| D1 | `ops_bus_events` + CHECKs | **PASS** |
| D2 | `lead_qualified` from disposition acked + audit | **PASS** |
| D3 | `wizard_started` CTA/beacon/ingest | **PASS** |
| D4 | `order_created` first-insert only | **PASS** (pytest) |
| D5 | audit chain | **PASS** |
| D6 | L2 pending; L3/L4 STOP + approve forbidden | **PASS** |
| D7 | Order PARKED EV-W2-010 | **PASS** (UI dogfood) |
| D8 | GET JWT; flag off → empty | **PASS** |
| D9 | typed UI trail · cache `vhq-w50a` | **PASS** (dogfood) |
| D10 | EV-W5-001…005 + pytest 9/9 | **PASS** |

## Dogfood verdict

- Sales ack → `lead_qualified` EV-W5-001  
- Wizard beacon/ingest → `wizard_started` EV-W5-002  
- MC flow: `last bus: wizard_started` + break EV-W2-010  
- Order Desk: **PARKED · EV-W2-010** · no fake LIVE  
- Evidence: `docs/handoffs/evidence-vhq-w50-dogfood/`

## Preserved (must not regress)

- Order Desk **PARKED · EV-W2-010**
- No silent L3/L4 · no Ads/Mollie execute · no free-form chat bus
- `VHQ_ROOMS` sole status SoT · HQ primary · 5 tabs
- Kill-switch `ops_bus_enabled`
- TELEGRAM_AUTOPUSH=0
- Prod tip unchanged until deploy GO: `6375ab1` / `vhq-w40c`

## Staging allowlist (COMMIT)

```text
agent/db.py
agent/ops_bus/
agent/nodes/brief_node.py
agent/nodes/order_node.py
api/routes/ops_bus.py
api/app.py
api/routes/commander.py
commander-ui/app.js
commander-ui/index.html
commander-ui/styles.css
commander-ui/sw.js
tests/unit/test_ops_bus.py
todo.json
.cursor/current-task.md
docs/handoffs/2026-07-31-VF-VHQ-W5-OPERATIONS-BUS-BLAST.md
docs/handoffs/2026-07-31-VF-VHQ-W5-OPERATIONS-BUS-PRECLOSE.md
docs/handoffs/2026-07-31-VF-VHQ-W5-OPERATIONS-BUS-FOUNDER-DOGFOOD.md
docs/handoffs/2026-07-31-VF-VHQ-W5-OPERATIONS-BUS-CLOSE.md
docs/handoffs/2026-07-31-SESSION-CLOSE-W5-VERIFY-PRECLOSE.md
docs/handoffs/evidence-vhq-w50-dogfood/
```

**Never stage:** `docs/ops/marketing/**`, MKT assets, unrelated old handoffs.

## Next (human GO required)

1. COMMIT allowlist (this session if requested — yes per closeout plan)  
2. Exact **`GO DEPLOY`** / **`GO jadzia-deploy`**  
3. `/jadzia-test` → `/audit-red-team` → `/jadzia-deploy`  
4. Prod dogfood `?v=vhq-w50a` → stamp  
5. W6 remains parked until separate GO after W5 prod stamp  

## STOP still held

- No Order Desk LIVE · no silent L3/L4 · no MKT · no deploy without GO  

CLOSE_VERDICT: **CLOSED** (local) · deploy GO separate
