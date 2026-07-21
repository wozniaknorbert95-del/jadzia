---
description: L3 - Automated Validation & Smoke Testing.
---

# /jadzia-test

## 🎯 Goal
Ensure the change is functionally correct and has not introduced regressions. This is the mandatory gate before any production deploy.

## 🛠️ Procedure

### 1. Automated Suite (The Hard Gate)
Run the following in order:
1. **Scoped style baseline**:
   `ruff check api/routes/design_agent.py agent/design_agent_service.py tests/unit/test_design_agent_route.py`
   and
   `black --check api/routes/design_agent.py agent/design_agent_service.py tests/unit/test_design_agent_route.py`
   $\to$ 0 errors. Repo-wide Ruff/Black debt is tracked separately and is not a
   global PASS condition.
2. **Scoped typing baseline**:
   `mypy api/routes/design_agent.py agent/design_agent_service.py --ignore-missing-imports --follow-imports=skip --disable-error-code=untyped-decorator`
   $\to$ 0 errors. Run Mypy on every additionally touched module and require no
   new errors there.
3. **Full regression suite**:
   `python -m pytest tests/ -v --cov=agent --cov=api --cov=core --cov=cli --cov-report=term-missing --cov-report=xml:coverage.xml`
   $\to$ 0 failed and a real `coverage.xml`. This is the canonical blocking CI
   command.
4. **Commander UI smoke**:
   `python -m pytest tests/test_api_integration.py::TestCommanderUiSmoke -q`
   $\to$ the locally bundled `/commander/` page returns 200 and contains
   `COI Commander`.

### 2. Smoke Testing (The "Real-World" Gate)
If the service layer was touched:
1. Start local server: `uvicorn main:app`.
2. Health Check: `curl -f localhost:8000/health`.
3. Feature Check: Execute the specific Telegram command or API call that triggers the new logic.
4. Log Audit: inspect `logs/jadzia.log` for unexpected warnings/errors.

### 3. Failure Handling
If any test fails:
- **STOP** the pipeline.
- Route immediately to `/debug`.
- Do NOT attempt "quick fixes" without a new `/debug` cycle.

## 📤 Output Format

```text
TEST_RESULT: [PASS | FAIL]
SCOPED_STYLE: [PASS | FAIL]
SCOPED_TYPE_CHECK: [PASS | FAIL]
PYTEST: [X passed, Y failed]
COMMANDER_SMOKE: [OK | FAIL - Detail]
REPO_WIDE_QUALITY_BASELINE: [EXISTING DEBT | N/A]

---
CURRENT_STAGE: L3-Validate
RECOMMENDED_NEXT: [/audit-red-team | /debug]
WHY_NEXT: PASS $\to$ Security audit; FAIL $\to$ Diagnostics.
---
```
