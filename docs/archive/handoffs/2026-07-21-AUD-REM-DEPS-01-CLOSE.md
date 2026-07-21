# Handoff — AUD-REM-DEPS-01 Dependency supply-chain remediation

**Date:** 2026-07-21  
**Task:** `AUD-REM-DEPS-01`  
**Status:** LOCAL PASS · GitHub Actions and VPS unverified  
**Git:** dirty shared `master` worktree · no commit, no push, no deploy

## Decision

- `pyproject.toml` is the only dependency declaration source and now explicitly
  supports CPython `>=3.11,<3.12`.
- `uv.lock` is the complete CPython 3.11 resolution (156 packages, including
  the declared development toolchain). `requirements.lock` is its hashed,
  production-only `uv export`; `requirements.txt` only delegates to that
  export for existing pip-based deployment scripts.
- ChromaDB was removed from the distribution. The advisory
  `PYSEC-2026-311` / `CVE-2026-45829` affects every currently published
  ChromaDB 1.x release through 1.5.9; resolver evidence showed no fixed
  `>=1.6.0` candidate. `campaign_memory` already treats Chroma as optional
  and preserves its SQL fallback, so no Chroma server/client is installed.

## CI controls

- All Python CI jobs install declared tools through `uv sync --locked
  --all-extras`; they cannot resolve unpinned test/lint tools separately.
- The security job runs `uv lock --check` and blocking
  `pip-audit --strict -r requirements.lock`.
- A separate required `gitleaks/gitleaks-action@v2` job blocks committed
  secrets on pushes and pull requests and receives the required
  `GITHUB_TOKEN`. If the repository is organization-owned, Dowódca must add
  the free `GITLEAKS_LICENSE` repository secret before the first GitHub run.
- `tests/test_dependency_lock_contract.py` has negative contracts for
  vulnerable ChromaDB, lock bypass, incomplete direct pins, and missing CI
  audit/secret controls.

## Evidence

```text
uv lock --upgrade --python 3.11
uv export --locked --no-dev --no-emit-project --output-file requirements.lock
```

Result: CPython `3.11.15`; `uv.lock` resolved 156 packages.

```text
uv pip install --python <fresh-cpython-3.11-venv> --require-hashes -r requirements.lock
```

Result: 85 runtime packages installed from a fresh environment. Imports of all
declared runtime dependencies passed; `chromadb` was absent. `uv pip check`
reported all installed packages compatible.

```text
uv lock --check
uvx pip-audit --strict -r requirements.lock
```

Result: lock check passed; `No known vulnerabilities found`.

```text
python -m pytest tests/test_dependency_lock_contract.py tests/unit/test_mb_f2b_memory.py -q
ruff check tests/test_dependency_lock_contract.py
black --check tests/test_dependency_lock_contract.py
python -m pytest tests/ -q
```

Result: focused `10 passed`; formatting/lint passed; full suite
`635 passed, 17 skipped, 1 xfailed` in 102.69 s.

## Residual risk / next

- Gitleaks and the updated dependency gates require an explicit commit/push
  before GitHub Actions can verify them. For an organization-owned repository,
  `GITLEAKS_LICENSE` is additionally required. This is not a production PASS.
- Do not reintroduce ChromaDB until a released fixed version is independently
  resolved and audited; retain SQL fallback in the meantime.
- Next isolated task: `AUD-REM-INGRESS-01`. No VPS/deploy action is authorized.
