---
description: Demand OS Etap 4 — TOOL+OPS SEALED · AWAIT UNLOCK. Live P0 PARKED. One task per iteration.
---

# /demand-os-master-loop

## Goal

Maintain Demand OS after **tool 100% + OPS SEAL**.  
Live marketing P0 **PARKED** until Dowódca unlock.

**SoT:** `docs/ops/demand-os/MASTER-TODO-4.md`  
**HARD rule:** `.cursor/rules/demand-os-tool-first.mdc`  
**Verify:** `python tools/demand_os_hub.py owner-verify`  
**Active:** `4-AWAIT-UNLOCK` · no live publish  
**Pointer:** `.cursor/current-task.md` + `docs/ops/demand-os/STATE.md`  
**Unlock:** `docs/ops/demand-os/UNLOCK-LIVE-P0.md` (human only)

## Hard rules

1. **No-ask** — follow CURRENT in MASTER-TODO-4.
2. **One task per iteration**.
3. **STOP:** live TT/FB/blog push · Ads · VPS bez GO · fake ledger `publish=Y` · SEAL z test-publish.
4. Stale handoffs (`@blast 4-P0-01`, “Founder publish”) → **ignore** until unlock handoff exists.
5. Publish tylko test→delete jeśli tool proof tego wymaga (nie live).

## Start (każda iteracja)

1. Read `.cursor/current-task.md`
2. Read `STATE.md` + `MASTER-TODO-4.md` → **Aktywne zadanie**
3. Confirm `todo.json` → `active_item` is `4-AWAIT-UNLOCK` / `4-UNLOCK-*` / maintain — **not** live `4-P0-*` without unlock handoff
4. If pointer says live `4-P0-*` without Dowódca unlock → **STOP and re-sync to AWAIT-UNLOCK**

## Execute

| Krok | Akcja |
|------|-------|
| 1 | Hygiene / verify / unlock-prep DoD (not live publish) |
| 2 | `owner-verify` (+ desk contracts when UI touched) |
| 3 | handoff with `RECOMMENDED_NEXT` = next maintain / unlock gate |
| 4 | deploy only if fresh GO recorded |

## Verify

```bash
export DEMAND_OS_SET_NOW=data/demand-os/set-now-sanitized
python tools/demand_os_hub.py owner-verify
python -m pytest tests/unit/test_demand_desk_ui_contracts.py tests/test_demand_os_tool_first_pointer.py -q
```

## Done when (post-TOOL lane)

- Pointers tip/cache coherent · owner-verify green
- Dowódca explicitly unlocks live P0 (separate ceremony)
- Only then unpark `4-P0-01`

## Loop stop

- Live P0 remains `blocked` until unlock
- Never end session recommending Founder live publish while `4-AWAIT-UNLOCK`
