---
status: "[PASS · HITL-READY DRY · marketing PARKED_LAST]"
updated: "2026-08-02"
gate: "DEMAND-OS-HITL-READY-00"
---

# HITL-READY tool (dry-only)

Maszyna gotowa na rytm Foundera — **bez** autonomicznego publish.

## DoD (PASS)

1. Desk contract SEALED (`DESK-CONTRACT.md` v2.1.1)
2. `GET …/demand-os/money-check` (read)
3. `POST …/demand-os/hitl/decision` GOTOWY|BLOKADA → calendar+audit · `publish: false`
4. `hub engage-dry` → ENGAGE-LOG → `hunt_queue.desk_status` SENT|BLOCK
5. `diagnostics.marketing_hitl_gate: BLOCKED` dopóki brak GO
6. RBAC: viewer nie mutuje hitl
7. doctor + pytest demand_os PASS

## Backend Trap (zakaz)

Po tym PASS **nie** otwieraj kolejnego „tool polish” gate.  
Jedyny next €: Founder `GO MARKETING HITL`.

## STOP

Live TT/FB · Ads · VPS · Etap 5 UI przed ≥1 tyg REAL.
