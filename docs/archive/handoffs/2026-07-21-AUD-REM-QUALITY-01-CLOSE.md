# Handoff — AUD-REM-QUALITY-01 quality baseline

**Date:** 2026-07-21  
**Task:** `AUD-REM-QUALITY-01`  
**Status:** LOCAL PASS · GitHub Actions unverified (no commit, no push, no deploy)  
**Scope:** truthful validation workflow, scoped Design Agent quality baseline, route regression guard, Commander UI smoke

## Decision

The repository-wide Ruff/Black/Mypy debt is not represented as a false green
gate. The executable validation workflow now documents the already scoped CI
baseline, runs the canonical full pytest command, and replaces the nonexistent
`tests/integration` command with a real Commander UI smoke test.

The small Design Agent scope was brought to zero errors without a repo-wide
format or typing sweep.

## Changes

1. `.agents/workflows/jadzia-test.md` now specifies:
   - scoped Ruff and Black checks;
   - scoped Mypy check;
   - full `pytest tests/` coverage command;
   - `TestCommanderUiSmoke` for the locally mounted `/commander/` UI.
2. `agent/design_agent_service.py` has typed JSON helpers, correctly ordered
   imports, and obsolete Mypy ignores removed.
3. `tests/unit/test_design_agent_route.py` is formatted and import-clean in the
   scoped CI baseline.
4. `tests/test_api_integration.py` verifies `/commander/` returns 200 and
   contains `COI Commander`.
5. `tests/test_quality_workflow_contract.py` prevents the test workflow from
   drifting back to the nonexistent integration folder or away from the
   canonical CI command.

## Evidence

```text
ruff check api/routes/design_agent.py agent/design_agent_service.py tests/unit/test_design_agent_route.py
black --check api/routes/design_agent.py agent/design_agent_service.py tests/unit/test_design_agent_route.py
mypy api/routes/design_agent.py agent/design_agent_service.py --ignore-missing-imports --follow-imports=skip --disable-error-code=untyped-decorator
```

Result: all scoped checks PASS.

```text
python -m pytest tests/test_quality_workflow_contract.py tests/test_ci_gate_contract.py tests/test_api_integration.py::TestCommanderUiSmoke tests/unit/test_design_agent_route.py -q
```

Result: `15 passed`.

```text
python -m pytest tests/ -v --cov=agent --cov=api --cov=core --cov=cli --cov-report=term-missing --cov-report=xml:coverage.xml
```

Result: `611 passed, 17 skipped, 1 xfailed, 857 warnings in 101.69s`;
real `coverage.xml` written; total coverage `63%`.

## Residual risk intentionally recorded

- Repo-wide baseline remains: Ruff 2,734 errors, Black 165 files, Mypy 734
  errors (audit snapshot). It is declared as existing debt, not a global PASS.
- GitHub Actions has not run on Python 3.11 because this task is uncommitted and
  unpushed.
- Production remains `UNVERIFIED`; no VPS or deploy action was performed.

## Next

Start `AUD-REM-CALLBACK-01` only as a separate 1-1-1 security task: callback
registry/allowlist, DNS and redirect validation, payload limits, log redaction,
and negative SSRF tests.
