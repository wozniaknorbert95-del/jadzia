---
name: debug
description: >-
  Five-step diagnostic with evidence for jadzia-core service/API issues.
  Use for Bugfix or before /context-reset when cause unknown.
disable-model-invocation: true
---

# /debug

## Goal

Root cause z dowodem przed naprawą.

## Canonical workflow

- **[.agents/workflows/debug.md](../../.agents/workflows/debug.md)**

## Output

```text
ISSUE: [...]
REPRO: [...]
ROOT_CAUSE: [...]
PROPOSED_FIX: [...]
VERIFICATION: [...]

---
CURRENT_STAGE: F4-Test
RECOMMENDED_NEXT: [/implement | /jadzia-test | /audit-red-team | /context-reset]
WHY_NEXT: [...]
---
```

**RECOMMENDED_NEXT:** Fix after approval → **`/jadzia-test`** then **`/audit-red-team`** before deploy.
