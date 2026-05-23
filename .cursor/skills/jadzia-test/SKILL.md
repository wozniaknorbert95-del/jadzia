---
name: jadzia-test
description: >-
  Run pytest and service smoke checks before audit or VPS deploy.
disable-model-invocation: true
---

# /jadzia-test

## Goal

Evidence that code passes automated tests and key endpoints before deploy gate.

## Canonical workflow

- **[.agents/workflows/jadzia-test.md](../../.agents/workflows/jadzia-test.md)**

## Output

```text
TEST_RESULT: [PASS | FAIL]
PYTEST: [summary]
SMOKE: [/health | webhook dry-run | NONE]

---
CURRENT_STAGE: F4-Test
RECOMMENDED_NEXT: [/audit-red-team | /debug | /implement]
WHY_NEXT: [...]
---
```
