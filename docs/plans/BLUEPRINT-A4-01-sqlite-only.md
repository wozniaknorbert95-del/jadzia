# BLUEPRINT-A4-01: SQLite-only Persistence

**Date:** 2026-06-26  
**Task:** A4-01  
**Decision:** SQLite is the single source of truth for session/task state.

## CURRENT_COUPLE

| Component | As-Is |
|-----------|-------|
| `save_state` | Always writes to SQLite via `_sync_to_sqlite` |
| `load_state` | SQLite first, JSON file fallback in `data/sessions/*.json` |
| `USE_SQLITE_STATE` | Env flag (default `0`); gates dashboard, list/cleanup |
| `cleanup_old_sessions` | SQLite when flag=1, plus JSON file scan always |
| `list_active_sessions` | SQLite when flag=1, else JSON file scan |
| Dashboard `/worker/dashboard` | Empty + `sqlite_required` when flag=0 |

## TARGET_STRUCTURE

```
load_state / save_state / clear_state
        |
        v
   agent/db.py  -->  jadzia.db (SQLite)
```

- No `USE_SQLITE_STATE` flag.
- No JSON session files as persistence (`data/sessions/*.json` not read/written).
- File locks (`data/sessions/.locks/`) remain for concurrency.
- `archive_state()` still writes JSON to `data/backups/` (operational backup only).
- `migrate_legacy_state()` one-shot: `.agent_state.json` -> SQLite.

## MIGRATION_STEPS

1. Remove `USE_SQLITE_STATE` from `_config.py` and all imports.
2. Simplify `load_state` to SQLite-only path.
3. Simplify `cleanup_old_sessions` and `list_active_sessions` to DB-only.
4. Remove dashboard/health JSON fallbacks.
5. Archive deprecated `scripts/restore_sessions_from_backup.py`.
6. Run full pytest suite.

## ROLLBACK

If VPS has sessions only in JSON files (pre-migration):

1. One-shot import: read each `data/sessions/*.json`, call `_sync_to_sqlite(chat_id, source, state)`.
2. Or restore from `data/backups/` JSON and import to SQLite.
3. Redeploy previous release tag if code rollback needed.

## REGRESSION_TESTS

- `tests/test_reliability_regression.py` — state round-trip, `_sync_to_sqlite`
- `tests/test_concurrent_tasks.py` — multi-chat isolation
- `tests/test_worker_api.py` — worker queue flow
- `tests/test_api_integration.py` — dashboard, health, sessions
- `tests/test_e2e_current.py` — load_state / save_state
- Full suite: `pytest tests/ -q`
