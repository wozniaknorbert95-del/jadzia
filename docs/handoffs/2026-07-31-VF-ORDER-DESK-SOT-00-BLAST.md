---
status: "[BLAST · READY — activate next session]"
gate: "VF-ORDER-DESK-SOT-00"
updated: "2026-07-31"
spec: "docs/superpowers/specs/2026-07-31-order-desk-sot-discovery-design.md"
plan: "docs/superpowers/plans/2026-07-31-order-desk-sot-discovery.md"
session_brief: "docs/handoffs/2026-07-31-SESSION-NEXT-ORDER-DESK-SOT.md"
runtime_changes_allowed: false
---

# BLAST — VF-ORDER-DESK-SOT-00

## Intent

Discovery SoT for Order Desk — odblokować przyszły S7 / EV-W2-010 **bez** budowania atrapy LIVE.

## Activate when

Next session start: set `todo.active_gate=VF-ORDER-DESK-SOT-00` and execute plan Tasks 0–4.

## STOP

Order LIVE · Mollie · Ads · runtime HQ Work View w tym gate · fake S7
