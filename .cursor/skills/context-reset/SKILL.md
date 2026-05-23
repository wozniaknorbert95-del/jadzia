---
name: context-reset
description: >-
  Saves session state and starts fresh chat after >2 failed attempts or context pollution.
disable-model-invocation: true
---

# /context-reset

## Canonical workflow

- **[.agents/workflows/context-reset.md](../../.agents/workflows/context-reset.md)**

## Output

```text
STATE_SAVED: [.cursor/session-state.md]
RESUME_PROMPT: [...]

---
CURRENT_STAGE: recovery
RECOMMENDED_NEXT: [new chat → /vibe-init]
WHY_NEXT: [...]
---
```
