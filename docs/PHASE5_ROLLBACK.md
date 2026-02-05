# Phase 5 Rollback (SQLite-only → Phase 4 dual-write)

## Phase 5 deployment

**Recommended:** Set `USE_SQLITE_STATE=1` in production so the app explicitly uses SQLite for state and behavior matches docs. If this env is unset, `load_state()` still tries SQLite first (so the server works and "No state found" is avoided), then falls back to JSON.

## Rollback to Phase 4

If you need to revert from Phase 5 (SQLite-only) back to Phase 4 (JSON + SQLite dual-write):

1. **Set env:** `USE_SQLITE_STATE=0` (or remove it so it defaults to 0).
2. **Restore JSON session files** from the backup taken before cutover:
   ```bash
   python scripts/restore_sessions_from_backup.py [YYYY-MM-DD]
   ```
   Use the backup date (e.g. `2025-02-04`) if you have multiple backups; otherwise the script uses the latest `data/sessions/backup_*` folder.
3. **Restart** the application.

After rollback, the app will read and write session state to `data/sessions/*.json` again; SQLite will no longer be used for state (unless you later set `USE_SQLITE_STATE=1`).

## Before Phase 5 cutover (backup)

Run once before deploying Phase 5 so you can restore if needed:

```bash
python scripts/backup_sessions_json.py
```

This creates `data/sessions/backup_YYYY-MM-DD/` and copies all `*.json` session files there.
