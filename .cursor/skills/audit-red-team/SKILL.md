---
name: audit-red-team
description: >-
  Adversarial pre-deploy audit for jadzia-core — report only, no patches.
  Gate before /jadzia-deploy.
disable-model-invocation: true
---

# /audit-red-team

## Goal

Luki security, SSH scope, webhook validation, DB safety przed deploy (Zasada 11).

## Canonical workflow

- **[.agents/workflows/audit-red-team.md](../../.agents/workflows/audit-red-team.md)**

## Don't

- Patch code during audit.
- PASS with CRITICAL open.

## Output

```text
VERDICT: [PASS ✅ | FAIL ❌]

---
CURRENT_STAGE: F4-Test
RECOMMENDED_NEXT: [/jadzia-deploy | /blast | /debug]
WHY_NEXT: [...]
---
```

**RECOMMENDED_NEXT:** **`/jadzia-deploy`** on PASS only — Commander executes.
