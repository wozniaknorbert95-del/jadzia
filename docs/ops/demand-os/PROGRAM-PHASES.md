---
status: "[ACTIVE · TOOL+OPS SEALED · live P0 PARKED]"
updated: "2026-08-03"
gate: "DEMAND-OS-MARKETING-4-00"
master_todo: "docs/ops/demand-os/MASTER-TODO-4.md"
sot_tool: "docs/ops/SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md"
desk_design: "docs/ops/demand-os/DEMAND-CONTROL-PANEL-DESIGN.md"
desk_contract: "docs/ops/demand-os/DESK-CONTRACT.md"
unlock: "docs/ops/demand-os/UNLOCK-LIVE-P0.md"
---

# Demand OS — kolejność (Dowódca — kanon)

**Tool 100% = maszyna + Biuro Popytu + każda zakładka Commander wypełniona.**  
**Live marketing dopiero po tool 100% + OPS hardening + jawnym unlock Dowódcy.**  
Publikacje wcześniej = tylko test → delete.

```text
ETAP 1   TOOL backend                    ← SEALED
ETAP 2   DESIGN v2.1                     ← ACCEPTED
ETAP 1b  DESK CONTRACT                   ← SEALED v2.1.1
ETAP 5   DASHBOARD build                 ← DEPLOYED
ETAP 5c  IA NAV                          ← DONE
ETAP 5d  IA SEAL                         ← DONE
ETAP 5e  gap-close (boot, Praca-first)   ← DONE
ETAP 5f  MASTER TODO dashboard 100%      ← SEALED 2026-08-03
ETAP 4   MARKETING                       ← env GO possible · live cadence PARKED
         TOOL 100%                       ← SEALED 2026-08-03
         OPS HARDENING                   ← SEALED 2026-08-03 floor a3deb59
         UX desk-dash09                  ← SEALED tip a8fdcf4 · AWAIT UNLOCK
```

## Etap 4 — Marketing HITL (**TOOL+OPS SEALED · live P0 PARKED**)

**SoT:** [`MASTER-TODO-4.md`](./MASTER-TODO-4.md)  
**Rule:** [`.cursor/rules/demand-os-tool-first.mdc`](../../../.cursor/rules/demand-os-tool-first.mdc)  
**TOOL SEAL:** [`2026-08-03-DEMAND-OS-TOOL-100-SEAL-CLOSE.md`](../handoffs/2026-08-03-DEMAND-OS-TOOL-100-SEAL-CLOSE.md)  
**OPS SEAL:** [`2026-08-03-DEMAND-OS-OPS-HARDENING-SEAL-CLOSE.md`](../archive/handoffs/2026-08-03-DEMAND-OS-OPS-HARDENING-SEAL-CLOSE.md)  
**Unlock:** [`UNLOCK-LIVE-P0.md`](./UNLOCK-LIVE-P0.md) (Dowódca only · env GO ≠ unlock)

- Tool residual **SEALED** · OPS hardening **SEALED** · doctor/footer/waves/connectors honest
- Live `4-P0-01/02/03` **PARKED** until Dowódca unlock ceremony
- `go_day_ready` = artifact score ≠ seal
- Ads **PARK cash** unchanged

## Etap 5f — SEALED (archiwum)

**Close:** [`2026-08-03-DEMAND-DESK-5F-CLOSE.md`](../archive/handoffs/2026-08-03-DEMAND-DESK-5F-CLOSE.md)
