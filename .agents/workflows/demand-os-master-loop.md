---
description: Demand OS Etap 5f — Master TODO loop. One task per iteration. No fake SEAL.
---

# /demand-os-master-loop

## Goal

Wykonuj **MASTER TODO Etap 5f** w pętli: jedno zadanie → prove → close → next.  
Domknij Commander Dashboard **100% per surface** bez ściemy.

**SoT:** `docs/ops/demand-os/MASTER-TODO-5F.md` (kanoniczny backlog)

## Hard rules

1. **No-ask** — wybierz pierwsze `open` w P0, potem P1.
2. **One task per iteration** — nie równoległe P0.
3. **STOP:** marketing live · Ads · VPS bez GO · fałszywy SEAL · commit set-now secrets.
4. **Nie dodawaj** nowych planów — aktualizuj MASTER-TODO status + pointer.

## Start (każda iteracja)

1. Read `MASTER-TODO-5F.md` → sekcja **Aktywne zadanie**
2. Read `STATE.md` + `.cursor/current-task.md`
3. Confirm `todo.json` → `active_gate: DEMAND-OS-DESK-5F-00`
4. If mismatch → Agent A sync first (15 min max)

## Execute

| Krok | Agent | Akcja |
|------|-------|-------|
| 1 | B | Implement per task DoD in MASTER-TODO |
| 2 | C | pytest gate + browser prod `?cb=desk-dashXX` |
| 3 | A | handoff + STATE + MASTER-TODO `[x]` + advance pointer |
| 4 | D | deploy only if GO recorded |

## Verify

```bash
export DEMAND_OS_SET_NOW=data/demand-os/set-now-sanitized
python tools/demand_os_hub.py doctor
python -m pytest tests/unit/test_demand_desk_ui_contracts.py tests/e2e/test_demand_desk_flow.py tests/test_hunt_dry_updates_queue.py -q
```

## Done when

- All P0 + P1 = `done` in MASTER-TODO
- Dowódca §8 = `done` (human)
- Hard DoD **15/15** · STATE `tool_100: SEALED`
- Handoff `DEMAND-DESK-5F-CLOSE.md`

## Loop stop

- `ready_for_human: Dowódca §8` when P0+P1 done
- Full SEAL when P2 complete
