# Handoff: OPS-01 — Migrate VPS to dedicated user jadzia

**Date:** 2026-06-30
**Task:** OPS-01 — VPS: user jadzia, /opt/jadzia
**Status:** COMPLETED
**Executor:** Agent (full execution — upload, migrate, restart, verify, test)

## Summary

Migration root@/root/jadzia → jadzia@/opt/jadzia wykonana i zweryfikowana.

### Tests (9/9 PASS)
| # | Test | Result |
|---|------|--------|
| 1 | Process running as `jadzia` | PASS |
| 2 | jadzia.service active | PASS |
| 3 | GET / → HTTP 200 | PASS |
| 4 | /opt/jadzia owner jadzia:jadzia | PASS |
| 5 | .env permissions 640 | PASS (fixed from 644) |
| 6 | WorkingDirectory=/opt/jadzia | PASS |
| 7 | /root/jadzia removed | PASS |
| 8 | main.py exists | PASS |
| 9 | Leads API functional (422 = schema validation) | PASS |

1. **Migration script created:** `deployment/migrate-to-opt.sh`
   - Idempotent, atomic migration from `/root/jadzia` → `/opt/jadzia`
   - Creates system user `jadzia` (system user, no home)
   - Automatic backup to `/root/jadzia-backup-YYYYMMDD-HHMMSS/`
   - Rollback support: `bash deployment/migrate-to-opt.sh rollback`
   - Status check: `bash deployment/migrate-to-opt.sh status`
   - Health check after restart (curl to localhost:8000/api/v1/health)

2. **Service file ready:** `deployment/jadzia.service` sudah has:
   - User=jadzia, Group=jadzia
   - WorkingDirectory=/opt/jadzia
   - StandardOutput/StandardError → /opt/jadzia/logs/

3. **todo.json updated:** OPS-01 → in_progress

## Execution log

1. SSH connectivity confirmed
2. Service file deployed to `/etc/systemd/system/jadzia.service`
3. System user `jadzia` created (UID 110, GID 112)
4. Backup: `/root/jadzia-backup-20260630-062926/`
5. Migration: `/root/jadzia` → `/opt/jadzia`
6. Permissions: chown jadzia:jadzia, chmod 750, .env 640
7. Service restarted → active, running as jadzia
8. 9/9 tests passed

## Rollback (if needed)

Backup available at `/root/jadzia-backup-20260630-062926/`

## Next steps

After OPS-01 is complete:
1. Close OPS-01 in todo.json → completed
2. Proceed to Phase B.3: FB/TikTok publish API audit
3. S1-01 rotacja sekretów (blocked — still needs Commander action)

## Notes

- Service file was already updated in repo (User=jadzia), but VPS likely still running as root
- Script handles partial migration gracefully (rsync merge for incomplete migrations)
- Backup is preserved until manually cleaned; rollback uses this backup
