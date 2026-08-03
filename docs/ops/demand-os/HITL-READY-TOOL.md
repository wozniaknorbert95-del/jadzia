---
status: "[PASS · HITL-READY DRY · HISTORICAL PRE-GO SNAPSHOT]"
updated: "2026-08-03"
gate: "DEMAND-OS-HITL-READY-00"
superseded_by: "docs/handoffs/2026-08-03-GO-MARKETING-HITL-EXEC-CLOSE.md"
---

# HITL-READY tool (dry-only)

Maszyna gotowa na rytm Foundera — **bez** autonomicznego publish.

## Historical note

Ten dokument opisuje **dry gate pre-GO** (HISTORICAL). Aktualny pointer = `MASTER-TODO-4.md` **`4-AWAIT-UNLOCK`** · TOOL+OPS SEALED · live P0 **PARKED**. Unlock: `UNLOCK-LIVE-P0.md`.

## DoD (PASS)

1. Desk contract SEALED (`DESK-CONTRACT.md` v2.1.1)
2. `GET …/demand-os/money-check` (read)
3. `POST …/demand-os/hitl/decision` GOTOWY|BLOKADA → calendar+audit · `publish: false`
4. `hub engage-dry` → ENGAGE-LOG → `hunt_queue.desk_status` SENT|BLOCK
5. `diagnostics.marketing_hitl_gate: BLOCKED` dopóki brak GO (env `DEMAND_OS_MARKETING_HITL=GO` → READY)
6. RBAC: viewer nie mutuje hitl
7. doctor + pytest demand_os PASS

## Backend Trap (zakaz)

Po tym PASS historycznie następował Founder `GO MARKETING HITL`.  
Po GO / seal: **nie** skacz do live P0. Tool 100% już SEALED; live P0 tylko po jawnym unlock Dowódcy (`UNLOCK-LIVE-P0.md`).

## STOP

Live TT/FB · Ads · VPS · Etap 5 UI przed ≥1 tyg REAL.
