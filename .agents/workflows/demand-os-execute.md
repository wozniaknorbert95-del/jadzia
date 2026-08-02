---
description: Demand OS — Etap 5f MASTER TODO loop (primary). Legacy 5b verify below.
---

# /demand-os-execute

## Primary runner

**Use:** [`/demand-os-master-loop`](./demand-os-master-loop.md)  
**SoT:** `docs/ops/demand-os/MASTER-TODO-5F.md`

## Goal (legacy verify path)

Maintain **desk backend + pytest gate** while 5f UI work proceeds.  
Marketing / live publish = **PARKED_LAST**.

## Hard rules

1. **No-ask** — follow MASTER-TODO pointer.
2. **STOP:** marketing live · Ads · VPS bez GO · fałszywy SEAL.
3. Nie skracaj: contract SEALED ≠ dashboard 100% per surface.

## Verify (maintain on each 5f session)

```bash
export DEMAND_OS_SET_NOW=data/demand-os/set-now-sanitized
python tools/demand_os_hub.py doctor
python -m pytest \
  tests/unit/test_demand_desk_ui_contracts.py \
  tests/test_demand_os_api_desk.py \
  tests/test_hunt_dry_updates_queue.py \
  tests/unit/test_render_desk_golden.py \
  tests/e2e/test_demand_desk_flow.py \
  tests/unit/test_commander_complete_ui.py \
  -q
```

Target: **100% PASS** · no regression.

## Done when (program)

- MASTER-TODO P0+P1 all `done`
- Dowódca §8 PASS
- Hard DoD **15/15** · STATE `tool_100: SEALED`
