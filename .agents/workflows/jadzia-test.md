---
description: pytest + smoke — gate before audit-red-team and deploy.
---

# /jadzia-test

## Goal

Automated verification per `.github/workflows/tests.yml` and local smoke.

## Procedure

1. Run `pytest` (full suite or scoped per BLAST).
2. Optional local: `uvicorn` + `curl localhost:8000/health` if service layer touched.
3. Record failures with evidence — route to `/debug` on FAIL.
4. On PASS → recommend `/audit-red-team` before any VPS deploy.

## Do

- Match CI workflow expectations
- Include failing test name + assertion on FAIL

## Don't

- Skip tests for "small" deploy
- Deploy on FAIL

## Output

```text
TEST_RESULT: [PASS | FAIL]
PYTEST: [N passed, M failed — or summary]
SMOKE: [/health OK | skipped | FAIL detail]

---
CURRENT_STAGE: F4-Test
RECOMMENDED_NEXT: [/audit-red-team | /debug]
WHY_NEXT: PASS → adversarial gate; FAIL → diagnose
---
```
