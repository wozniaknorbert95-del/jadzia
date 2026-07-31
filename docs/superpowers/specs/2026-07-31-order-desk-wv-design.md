---
status: "[SPEC · BUILD]"
title: "VF-ORDER-DESK-WV-00 — thin read-only Order Desk Work View"
updated: "2026-07-31"
gate: "VF-ORDER-DESK-WV-00"
depends_on: "VF-ORDER-DESK-SOT-00 ACCEPTED"
sot: "docs/ops/ORDER-DESK-SOT-v0.md"
runtime_changes_allowed: true
cache: "vhq-w68a"
---

# Design: VF-ORDER-DESK-WV-00

## Goal

Thin **read-only** Order Desk Work View: show INT-002 mirror rows with honesty that desk is still **PARKED · EV-W2-010**. No LIVE KPI, no disposition CTAs, no ops_state invent.

## Approach (chosen)

**A — Mirror projection in existing Work panel** (recommended): extend `/api/v1/orders` list fields; render table in `#vhq-work-order`; keep room `status=PARKED`.

Rejected: B invent ops_state table now (mega) · C claim LIVE from row count (fake S7).

## DoD

| ID | Pass |
|----|------|
| W1 | Mirror list section in Order Work View (JWT) |
| W2 | Fields: order_id, class, WC status, pay, gross, ingested, ops=`insufficient_data` |
| W3 | Empty / no-session honesty (no fake 0 open-orders) |
| W4 | Room stays PARKED · EV-W2-010 · no primary fulfil CTA |
| W5 | Contract tests + cache `vhq-w68a` |
| W6 | PRECLOSE — deploy only with GO DEPLOY |

## STOP

Unpark EV-W2-010 · S7=5 · Mollie · Accept/Ship buttons · reopen FINAL nav · stage MKT/
