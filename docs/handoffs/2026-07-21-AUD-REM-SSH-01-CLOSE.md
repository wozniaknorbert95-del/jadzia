# Handoff — AUD-REM-SSH-01 SSH trust and archive safety

**Date:** 2026-07-21  
**Task:** `AUD-REM-SSH-01`  
**Status:** LOCAL PASS · GitHub Actions and VPS unverified  
**Git:** `master` @ `29043cb` · dirty worktree · no commit, no push, no deploy

## Done

1. Added strict Paramiko host-key policy in `agent/tools/ssh_host_policy.py`:
   system/dedicated known-hosts loading, `RejectPolicy`, optional
   `SSH_HOST_KEY_FINGERPRINT` SHA256 pin verification.
2. Replaced `AutoAddPolicy` in `ssh_pure.py` and the WP Explorer connector.
3. Added `safe_extractall()` and replaced unsafe `tar.extractall()`; traversal,
   symlinks, hard links, and device members are rejected.
4. Hardened `list_files()` with safe base-path validation and `shlex.quote`;
   filename globs with path separators are rejected before SSH command execution.
5. Documented `SSH_KNOWN_HOSTS_PATH` and `SSH_HOST_KEY_FINGERPRINT` in
   `.env.example`.

## Evidence

```text
python -m pytest tests/test_ssh_pure.py tests/unit/test_ssh_security.py -q
```

Result: `11 passed`.

```text
ruff check agent/tools/ssh_host_policy.py agent/tools/safe_archive.py tests/unit/test_ssh_security.py
black --check agent/tools/ssh_host_policy.py agent/tools/safe_archive.py tests/unit/test_ssh_security.py
```

Result: PASS.

```text
python -m pytest tests/ -v --cov=agent --cov=api --cov=core --cov=cli --cov-report=term-missing --cov-report=xml:coverage.xml
```

Result: `630 passed, 17 skipped, 1 xfailed, 862 warnings in 117.18s`;
real `coverage.xml` written; total coverage `63%`.

## Left / risks

- A production SSH host fingerprint/known_hosts record must be collected only
  after fresh human VPS GO. Until then, production remains `UNVERIFIED`.
- Full-file Ruff debt remains intentionally outside this task; the new SSH
  security files are clean.
- All remediation changes remain uncommitted in the shared `master` worktree.

## Next

`AUD-REM-DEPS-01` is the next separate 1-1-1 task: authoritative dependency
source, complete Python 3.11 lock, Chroma mitigation, clean-install proof, and
blocking dependency/secret checks. Do not run VPS or deploy actions.
