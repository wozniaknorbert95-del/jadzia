---
status: "[STAMPED-PASS]"
title: "VF-VHQ-W5 — local Founder dogfood PASS"
updated: "2026-07-31"
gate: "VF-VHQ-W5-OPERATIONS-BUS"
cache: "vhq-w50a"
local_url: "http://127.0.0.1:8000/commander/?v=vhq-w50a"
jwt: true
pytest_ops_bus: "9/9 PASS"
prod_tip_unchanged: "6375ab1 / vhq-w40c"
stamp_by: "agent-on-Founder-closeout-delegation (kompleksowe DOMKNIĘCIE)"
---

# VF-VHQ-W5 — local Founder dogfood PASS

**Local URL:** `http://127.0.0.1:8000/commander/?v=vhq-w50a`  
**Auth:** JWT (role `dowodca`) · same-origin Commander mount  
**Evidence dir:** `docs/handoffs/evidence-vhq-w50-dogfood/`

---

## Checklist

| # | Step | Expected | Result |
|---|------|----------|--------|
| 1 | Open `?v=vhq-w50a` | Cache hint `vhq-w50a` | **PASS** |
| 2 | Sales disposition `acked` (lead_id=1) | `lead_qualified` EV-W5-001 on bus | **PASS** |
| 3 | Wizard beacon / ingest | `wizard_started` EV-W5-002 | **PASS** |
| 4 | Wizard room bus cards | typed trail both hops · no chat workflow | **PASS** |
| 5 | Mission Control flow break | EV-W2-010 + `last bus: wizard_started` | **PASS** |
| 6 | Order Desk | PARKED · EV-W2-010 · no LIVE desk | **PASS** |
| 7 | No silent L3/L4 / no Ads/Mollie / no MKT dirty | honored | **PASS** |
| 8 | pytest `tests/unit/test_ops_bus.py` | 9/9 | **PASS** |

---

## API spine (local)

```text
GET /api/v1/commander/ops-bus/events → total=2 enabled=true
  wizard_started  EV-W5-002  L0/none
  lead_qualified  EV-W5-001  L1/none
POST .../leads/1/disposition {acked} → ok
POST .../ops-bus/ingest {wizard_started} → ok duplicate=false
```

## Screenshots

| File | View |
|------|------|
| `w50-00-sales-room.png` | Sales · flow Sales→Wizard→Order PARKED |
| `w50-01-wizard-ops-bus.png` | Wizard · Operations Bus typed cards |
| `w50-02-mc.png` | Mission Control · last bus + EV-W2-010 |
| `w50-03-order-parked.png` | Order Desk PARKED · EV-W2-010 |

## Stamp

```text
FOUNDER STAMP: PASS
Date: 2026-07-31
Notes: Local JWT dogfood vhq-w50a. Sales ack → wizard_started → Order PARKED EV-W2-010. Deploy GO separate (Zasada 11).
```
