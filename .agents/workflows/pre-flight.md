---
description: Fast-track checklist before Hotfix or Deploy — jadzia-core.
---

# pre-flight

## When

Hotfix or Deploy classification from `/vibe-init`.

## Checklist

- [ ] `git status -sb` — know branch and dirty state
- [ ] `todo.json` — active task id identified
- [ ] **Deploy only:** DB backup step documented (see [jadzia-deploy.md](jadzia-deploy.md))
- [ ] **Deploy only:** `/jadzia-test` green locally or on CI
- [ ] No secrets in diff (`.env`, keys, tokens)
- [ ] Zasada 11 acknowledged — Commander executes VPS commands

## Output

```text
PRE_FLIGHT: PASS | FAIL
BLOCKERS: [NONE | ...]

---
CURRENT_STAGE: F1-Plan | F5-Launch
RECOMMENDED_NEXT: [/implement | /jadzia-test | /jadzia-deploy]
WHY_NEXT: [...]
---
```
