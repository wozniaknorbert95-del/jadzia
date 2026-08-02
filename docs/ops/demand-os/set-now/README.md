---
status: "[HITL-READY DRY · marketing PARKED_LAST]"
title: "Demand OS — SET NOW artifacts"
updated: "2026-08-02"
gate: "DEMAND-OS-HITL-READY-00"
os_target: "docs/ops/SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md §C"
---

# SET NOW Pack

**SoT egzekucji:** [`../../SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md`](../../SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md)  
**Marketing HITL:** PARKED_LAST · Ads = PARK cash

| Plik | Rola | OS |
|------|------|-----|
| [`GO-DAY-TODAY.md`](./GO-DAY-TODAY.md) | TOOL FIRST tip | O |
| [`ADS-FREEZE.md`](./ADS-FREEZE.md) | F5 parked_cash | C.1 #5 |
| [`LEDGER.csv`](./LEDGER.csv) | ledger | C.7 |
| [`CONTENT-CALENDAR.json`](./CONTENT-CALENDAR.json) | growth gate F2 | E |
| [`MEMORY.json`](./MEMORY.json) | §F memory | F |
| [`A2A-HANDOFFS.jsonl`](./A2A-HANDOFFS.jsonl) | §E A2A | E |
| [`GROWTH-EVENTS.jsonl`](./GROWTH-EVENTS.jsonl) | F1 events | F1 |
| [`MONEY-CHECK-OPS.md`](./MONEY-CHECK-OPS.md) | Pon rytm | C.1 #8 |
| [`VALIDATOR-LOG.csv`](./VALIDATOR-LOG.csv) | Val log | C.5 |
| Organic sprint / hunt / captions | **PARKED_LAST** | — |

## Operator dry runbook (no live)

1. `python tools/demand_os_hub.py money-check`  
2. F2 validate asset → calendar `validated`  
3. HITL decide: API `POST …/hitl/decision` GOTOWY|BLOKADA (no publish)  
4. `hub engage-dry` → ENGAGE-LOG → `status` hunt_queue SENT|BLOCK  
5. Live publish dopiero po `GO MARKETING HITL`

**Verify:** `python tools/demand_os_phase0_check.py` · `hub doctor` · `hub status`  
**Runner:** `/demand-os-execute` · [`../STATE.md`](../STATE.md)  
**Deploy / live publish:** STOP
