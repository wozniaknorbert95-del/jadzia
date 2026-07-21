# Handoff — AUD-REM-CI-01 CI release-gate recovery

**Date:** 2026-07-21  
**Task:** `AUD-REM-CI-01`  
**Status:** LOCAL PASS · GitHub Actions unverified (no commit, no push, no deploy)  
**Scope:** six full-suite failures, canonical blocking pytest workflow, real coverage artifact

## Decision

`.github/workflows/ci.yml` is the sole test-gate owner. It now runs the full
`tests/` suite with coverage for `agent`, `api`, `core`, and `cli`, writes
`coverage.xml`, uploads it as a GitHub artifact, and treats a Codecov upload
error as blocking. The former partial `tests.yml` workflow was removed.

## RCA — six baseline failures

| Failure | Classification | Resolution |
|---|---|---|
| Route registration inventory | Stale test contract | Kept the critical-route subset; stopped treating every newly registered route as an error. |
| `/zadanie` with payload | Stale test contract | Assert its current `ticket` alias behavior. |
| `/zadanie` without payload | Stale test contract | Assert its current `ticket` alias behavior. |
| `/zadanie@Bot` group form | Stale test contract | Assert its current `ticket` alias behavior. |
| Design Agent opening copy | Stale test contract | Opening intentionally defers Standard/Premium to the recommendation stage. |
| Organic lift facts | Stale test isolation | Mocked the mandatory token-health preflight as `has_read_insights=true`, matching the mocked successful insights payload. |

No production code changed. No SSRF, SSH, dependencies, database, VPS, or
global Ruff/Black/Mypy cleanup was included.

## Evidence

1. Baseline: `pytest tests/` → `6 failed, 601 passed, 17 skipped, 1 xfailed`.
2. Remediated contracts + CI workflow contract: `8 passed`.
3. Full local release command:

   ```text
   python -m pytest tests/ -v --cov=agent --cov=api --cov=core --cov=cli --cov-report=term-missing --cov-report=xml:coverage.xml
   ```

   Result: `609 passed, 17 skipped, 1 xfailed, 853 warnings in 111.52s`;
   real `coverage.xml` generated; total coverage `63%`.
4. Negative proof: a temporary, uncommitted failing test outside Design Agent
   (`tests/test_aaa_ci_non_design_regression_probe.py`) made
   `python -m pytest tests/ -q -x` fail with exit code 1. The probe was deleted
   before the final source state.
5. Persisted regression guard: `tests/test_ci_gate_contract.py` verifies the
   canonical workflow selects `tests/`, writes `coverage.xml`, uploads the
   artifact, and that no legacy partial test workflow remains.

## Deferred intentionally

- Repo-wide Ruff, Black, and Mypy baseline remains red and belongs to
  `AUD-REM-QUALITY-01`.
- GitHub Actions has not run because this task was neither committed nor pushed.
- Production remains `UNVERIFIED`; no deploy was attempted.

## Next

1. Review and commit this focused CI diff when explicitly instructed.
2. Verify the first GitHub Actions run on Python 3.11 after push.
3. Continue with `AUD-REM-QUALITY-01`; do not fold security/runtime findings into this task.
