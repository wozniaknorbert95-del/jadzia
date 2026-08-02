---
description: Demand OS — Etap 5b hardening. Marketing PARKED_LAST until Dowódca §8 prod + GO deploy.
---

# /demand-os-execute

## Goal

Domknąć **tool 100% UI** = backend SEALED + **Biuro Popytu dashboard hardened (Etap 5b)**.  
Marketing / live publish = **PARKED_LAST** — dopiero po Dowódca §8 prod + deploy GO.

SoT: `PROGRAM-PHASES.md` · design `DEMAND-CONTROL-PANEL-DESIGN.md` · API `DESK-CONTRACT.md` · spec `docs/superpowers/specs/2026-08-02-demand-desk-hardening-design.md`.

## Hard rules

1. **No-ask** — next = Etap 5b verify + Dowódca §8 prod unless gate zmieni Dowódca.
2. **STOP:** marketing live · Ads · VPS bez GO · fałszywy SEAL przed Hard DoD 15/15.
3. Nie skracaj: contract SEALED ≠ tool 100% UI SEALED.

## Procedure

1. Hydrate STATE + design + DESK-UI-HANDOFF + 5b spec  
2. `DEMAND_OS_SET_NOW=data/demand-os/set-now-sanitized hub doctor` + pytest desk suite  
3. Verify dashboard surface (`#view-demand-desk` · cache `desk-dash03`)  
4. Tip STATE · handoff `DEMAND-DESK-5B-CLOSE.md`  

## Verify (agent gate)

```bash
DEMAND_OS_SET_NOW=data/demand-os/set-now-sanitized python tools/demand_os_hub.py doctor
DEMAND_OS_SET_NOW=data/demand-os/set-now-sanitized python -m pytest \
  tests/unit/test_demand_desk_ui_contracts.py \
  tests/test_demand_desk_api_extended.py \
  tests/test_demand_os_api_desk.py \
  tests/test_demand_os_desk_contract.py \
  tests/test_hunt_dry_updates_queue.py \
  tests/test_hitl_decision_persists.py \
  tests/unit/test_render_desk_golden.py \
  tests/unit/test_demand_os_status_readonly.py \
  tests/e2e/test_demand_desk_flow.py \
  tests/unit/test_commander_complete_ui.py \
  tests/unit/test_vhq_firm_ia_contracts.py -q
```

Target: **≥75 desk-related tests PASS**.

## Done when

- Hard DoD **14/15 agent PASS** (#12 Dowódca §8 prod pending)
- Dashboard strefy A0–F wired · layout AB/CD · desk-dash03
- Prod deploy + set-now sync tylko z **`GO DEPLOY COMMANDER UI`**
- marketing nadal **PARKED_LAST**
