---
description: Demand OS Etap 4 — TOOL FIRST loop. Live P0 PARKED. One task per iteration.
---

# /demand-os-master-loop

## Goal

Domknij **narzędzie 100%** (`4-TOOL-*`).  
Live marketing P0 **PARKED** aż do jawnego unlock Dowódcy.

**SoT:** `docs/ops/demand-os/MASTER-TODO-4.md`  
**HARD rule:** `.cursor/rules/demand-os-tool-first.mdc`  
**Verify:** `python tools/demand_os_hub.py owner-verify`  
**Active:** `4-AWAIT-UNLOCK` · unlock preflight PASS · no live publish  
**Pointer:** `.cursor/current-task.md` + `docs/ops/demand-os/STATE.md`  
**Unlock:** `docs/ops/demand-os/UNLOCK-LIVE-P0.md` (human only)

## Hard rules

1. **No-ask** — follow CURRENT in MASTER-TODO-4 (tool residual).
2. **One task per iteration**.
3. **STOP:** live TT/FB/blog push · Ads · VPS bez GO · fake ledger `publish=Y` · SEAL z test-publish.
4. Stale handoffs (`@blast 4-P0-01`, “Founder publish”) → **ignore**.
5. Publish tylko test→delete jeśli tool proof tego wymaga.

## Start (każda iteracja)

1. Read `.cursor/current-task.md`
2. Read `STATE.md` + `MASTER-TODO-4.md` → **Aktywne zadanie**
3. Confirm `todo.json` → `active_item` starts with `4-TOOL-`
4. If pointer says live `4-P0-*` without Dowódca unlock → **STOP and re-sync to TOOL FIRST**

## Execute

| Krok | Akcja |
|------|-------|
| 1 | Implement tool residual DoD |
| 2 | `doctor` + `pytest -k demand_os` |
| 3 | handoff with `RECOMMENDED_NEXT` = next **tool** item |
| 4 | deploy only if fresh GO recorded |

## Verify

```bash
export DEMAND_OS_SET_NOW=data/demand-os/set-now-sanitized
python tools/demand_os_hub.py doctor
python -m pytest tests -k demand_os -q
```

## Done when (tool lane)

- Tool residual closed per MASTER-TODO-4 `4-TOOL-*`
- Dowódca explicitly unlocks live P0 (separate ceremony)
- Only then unpark `4-P0-01`

## Loop stop

- Live P0 remains `blocked` until unlock
- Never end session recommending Founder live publish while tool open
