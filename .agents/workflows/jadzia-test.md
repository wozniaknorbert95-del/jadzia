---
description: L3 - Automated Validation & Smoke Testing.
---

# /jadzia-test

## 🎯 Goal
Ensure the change is functionally correct and has not introduced regressions. This is the mandatory gate before any production deploy.

## 🛠️ Procedure

### 1. Automated Suite (The Hard Gate)
Run the following in order:
1. **Linting**: `ruff check .` $\to$ Must be 0 errors.
2. **Typing**: `mypy .` $\to$ No new type errors in touched modules.
3. **Unit Tests**: `pytest tests/unit` $\to$ All tests must pass.
4. **Integration**: `pytest tests/integration` $\to$ Verify the full flow (API $\to$ DB).

### 2. Smoke Testing (The "Real-World" Gate)
If the service layer was touched:
1. Start local server: `uvicorn main:app`.
2. Health Check: `curl -f localhost:8000/health`.
3. Feature Check: Execute the specific Telegram command or API call that triggers the new logic.
4. Log Audit: `tail -f logs/jadzia.log` $\to$ Check for unexpected warnings/errors.

### 3. Failure Handling
If any test fails:
- **STOP** the pipeline.
- Route immediately to `/debug`.
- Do NOT attempt "quick fixes" without a new `/debug` cycle.

## 📤 Output Format

```text
TEST_RESULT: [PASS | FAIL]
LINT: [PASS | FAIL]
TYPE_CHECK: [PASS | FAIL]
PYTEST: [X passed, Y failed]
SMOKE_TEST: [OK | FAIL - Detail]

---
CURRENT_STAGE: L3-Validate
RECOMMENDED_NEXT: [/audit-red-team | /debug]
WHY_NEXT: PASS $\to$ Security audit; FAIL $\to$ Diagnostics.
---
```
