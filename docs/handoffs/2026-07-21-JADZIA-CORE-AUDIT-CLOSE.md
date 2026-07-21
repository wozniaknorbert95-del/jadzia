# Handoff — Jadzia Core system audit

**Date:** 2026-07-21  
**Task:** `NEW-AUDIT-2026-07-21`  
**Baseline:** local `master` @ `29043cb76aea934ab74d263655383f0787876311`  
**Status:** AUDIT COMPLETE · REMEDIATION NOT STARTED  
**Decision:** `FAIL repo gate` · `UNVERIFIED production` · `NO DEPLOY`

## Delivered

- Canonical report: `docs/ops/JADZIA-CORE-AUDIT-2026-07-21.md`
- Interactive Canvas: `jadzia-core-audit-2026-07-21.canvas.tsx`
- Local evidence: architecture/auth/data/runtime/CI/dependencies/ops/SoT review
- Prioritized remediation backlog in 1-1-1 slices
- VPS validation parked as `READY_FOR_HUMAN` pending fresh GO

## Hard evidence

| Check | Result |
|---|---|
| Test inventory | 625 collected |
| Full pytest + coverage | 6 failed, 601 passed, 17 skipped, 1 xfailed |
| Coverage | 63% |
| Exact CI test gate | 14 passed |
| Ruff | 2,734 errors |
| Black | 165 files would reformat |
| Mypy | 734 errors in 97/160 source files |
| Bandit | 4 high, 18 medium |
| pip-audit | `chromadb 1.5.9` / `PYSEC-2026-311` |
| Lock completeness | 13/18 direct dependencies |

## Release blockers

1. CI validates 14/625 tests while the full suite is red.
2. Worker callback accepts arbitrary URLs (SSRF after authorized task creation).
3. Active SSH paths use `AutoAddPolicy`.
4. Partial multi-file write can be marked `COMPLETED`.
5. Runtime health callbacks are not wired to the metrics object read by health API.

## Next 1-1-1 task

`AUD-REM-CI-01`: make the real regression suite a blocking gate and fix/triage the
six current failures. Do not combine SSRF, SSH or dependency remediation into this
same diff.

## READY_FOR_HUMAN

Fresh GO is required before read-only VPS evidence:

- `/opt/jadzia` tip/process count and active systemd unit
- external auth/OpenAPI/health HTTP codes
- SQLite `integrity_check` and journal mode
- active nginx/firewall and port 8000 exposure
- backup evidence and rolling OPS-AI re-measure
- confirmation that Chroma is embedded-only

No production connection, deploy, secret read, external LLM call or marketing action
was performed in this audit.
