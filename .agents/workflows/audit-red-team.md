---
description: Audyt adversarial przed deploy VPS — raport only.
---

# /audit-red-team

## Goal

Security, SSH least privilege, webhook secrets, SQLite migrations, error handling — **bez patchy**.

## Do

- Priorytety: CRITICAL / HIGH / MEDIUM / LOW.
- Check: no secrets in repo, Paramiko scope, HITL (Tak/Nie), rollback path in [PRD-core.md](../../docs/PRD-core.md).
- PASS/FAIL explicit.

## Don't

- Patch during audit.
- Deploy autonomously.

## Output

```text
VULNERABILITIES: [...]
REGRESSION_RISK: [Low|Med|High]
VERDICT: [PASS ✅ | FAIL ❌]

---
CURRENT_STAGE: F4-Test
RECOMMENDED_NEXT: [/jadzia-deploy | /blast | /debug]
WHY_NEXT: [...]
---
```
