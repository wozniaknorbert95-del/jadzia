---
status: DONE
date: 2026-08-03
gate: DEMAND-OS-MARKETING-4-00
next_item: 4-TOOL-01
---

# Handoff — Direction correction: TOOL FIRST

## Why

Dowódca: Cursor ciągle pchał w live publish (`4-P0-01`), mimo twardej intencji **najpierw narzędzie 100%**; publikacje tylko testowo.

Przyczyna dryfu: handoffy/`@blast 4-P0-01` + MASTER pointer po GO LIVE traktowały P0 publish jako „next”, bez twardej reguły TOOL FIRST.

## What Was Done

- AlwaysApply rules (repo + user):
  - `jadzia-core/.cursor/rules/demand-os-tool-first.mdc`
  - `~/.cursor/rules/demand-os-tool-first.mdc`
- `AGENTS.md` (repo + `C:/Users/FlexGrafik/AGENTS.md`) + `jadzia-core.mdc`
- SoT / workflows / brain / scorecard / todo pointers → `4-TOOL-01`
- Superseded stale handoffs that said Founder publish / `@blast 4-P0-01`
- Regression test: `tests/test_demand_os_tool_first_pointer.py`

## Policy (remember)

1. Tool 100% first  
2. Publish only test → delete when needed for tool proof  
3. Live marketing only after explicit Dowódca unlock  

## Next

Continue Demand OS **tool residual / 100%**. Do not ask Founder to publish live TT.

```text
DONE: [tool-first rule + SoT correction; live P0 PARKED]
LEFT: [4-TOOL-01 residual tool work; optional test-publish+delete plan if tool needs proof]
RISKS: [stale handoffs may still say Founder publish — ignore unless unlock]
V-FILES: [.cursor/rules/demand-os-tool-first.mdc | docs/ops/demand-os/MASTER-TODO-4.md | AGENTS.md]
NEXT_COMMAND_FOR_NEW_AGENT: [@blast 4-TOOL-01 · tool residual only · no live publish]

---
CURRENT_STAGE: F6-Iterate
RECOMMENDED_NEXT: @blast 4-TOOL-01
WHY_NEXT: Direction locked; resume tool 100%, not marketing cadence.
---
```
