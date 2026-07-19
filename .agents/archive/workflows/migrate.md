---
description: L1-Migrate - High-Risk SQLite Schema Transition (archived — golden path uses inline migrations).
---

# /migrate (archived)

> **Archived** to `.agents/archive/workflows/`. Golden path: inline migrations in `agent/db.py`, single DB path `data/jadzia.db`.

## Goal

Perform a controlled, reversible change to the SQLite database schema or data.

## SQLite path (SoT)

- **File:** `data/jadzia.db` (see `agent/db.py` → `DB_PATH`)
- **Mechanism:** inline `_migrate_*` functions called from `_init_schema`; no external migration tool, no second DB path.

## Safety gate (3-point backup)

Before applying:

- [ ] Local DB backup created (`cp data/jadzia.db data/jadzia.db.bak.YYYYMMDD-HHMMSS`).
- [ ] VPS DB backup planned (Commander execution).
- [ ] Rollback = restore backup file (no downgrade revision).

## Execution (1-1-1)

- One migration per session.
- One schema change at a time.
- One verification test per change.

## Post-migration validation

- **Integrity:** `PRAGMA integrity_check;`
- **Data audit:** existing records intact.
- **App test:** worker loop read/write OK.

## Output format

```text
MIGRATION_ID: [function name in agent/db.py]
BACKUP_STATUS: [CONFIRMED]
SCHEMA_CHANGE: [Brief description]
VALIDATION_RESULT: [PASS | FAIL]

---
CURRENT_STAGE: L1-Migrate
RECOMMENDED_NEXT: /jadzia-test
---
```
