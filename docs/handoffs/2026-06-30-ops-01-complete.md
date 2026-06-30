# Handoff: OPS-01 — Migrate VPS to dedicated user jadzia

**Date:** 2026-06-30
**Task:** OPS-01 — VPS: user jadzia, /opt/jadzia
**Status:** COMPLETED
**/jadzia-test:** COMPLETED (342/342 pytest PASS, 9/9 migration PASS, 7/7 open smoke PASS, 3/3 auth-gated correct 401)
**Executor:** Agent (full execution — upload, migrate, restart, verify, test)

## What changed

AS-IS: root@/root/jadzia, User=root in service file
TO-BE: jadzia@/opt/jadzia, User=jadzia in service file

## Execution log

1. SSH to VPS — confirmed running as root, /root/jadzia active
2. Backup system user jadzia created (UID 110, GID 112)
3. Service file deployed to /etc/systemd/system/jadzia.service
4. Backup: /root/jadzia → /root/jadzia-backup-20260630-062926/
5. Migration: /root/jadzia → /opt/jadzia (nested dir issue fixed)
6. Permissions: chown jadzia:jadzia, chmod 750, .env 640
7. Service restarted → active, PID 3664156, running as jadzia
8. All tests passed

## Test results

### pytest (local)
342 passed, 1 skipped, 1 xfailed — 0 failures

### VPS smoke tests (open endpoints)
- GET / → 200 OK ✓
- GET /worker/health → 200 OK ✓
- GET /costs → 200 OK ✓
- GET /sessions → 200 OK ✓
- GET /status → 200 OK ✓
- POST /api/v1/leads → 422 (schema validation, expected) ✓
- jadzia.db accessible ✓

### VPS smoke tests (auth-required endpoints — correct 401)
- GET /worker/dashboard → 401 (JWT required) ✓
- GET /api/v1/content-calendar → 401 (JWT required) ✓
- GET /api/v1/analytics/snapshot → 401 (JWT required) ✓

### Migration integrity (9/9)
- Process user: jadzia ✓
- Service active ✓
- GET / → 200 ✓
- /opt/jadzia owner: jadzia:jadzia ✓
- .env permissions: 640 ✓
- WorkingDirectory: /opt/jadzia ✓
- /root/jadzia removed ✓
- main.py exists ✓
- venv python executable ✓

## Rollback

Backup available: /root/jadzia-backup-20260630-062926/

## Next tasks

1. Phase B.3: FB/TikTok publish API audit (next_agent)
2. S1-01: Rotacja sekretów (BLOCKED — needs Commander to generate new keys)
