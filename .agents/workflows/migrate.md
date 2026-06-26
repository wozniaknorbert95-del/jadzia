---
description: L1-Migrate - High-Risk State Transition.
---

# /migrate

## 🎯 Goal
Perform a controlled, reversible change to the SQLite database schema or data.

## 🛠️ The Migration Pipeline

### 1. Schema Design
- Define the `alembic` revision.
- Verify that the change is backward-compatible (if possible) or requires a full stop.

### 2. The Safety Gate (The 3-Point Backup)
Before applying:
- [ ] Local DB backup created.
- [ ] VPS DB backup planned (Commander execution).
- [ ] Rollback script (`alembic downgrade -1`) tested locally.

### 3. Execution (The 1-1-1 Rule)
- One migration per session.
- One version jump at a time.
- One verification test per change.

### 4. Post-Migration Validation
- **Integrity Check**: Run `PRAGMA integrity_check;`.
- **Data Audit**: Verify that existing records were not corrupted during the transition.
- **App Test**: Ensure the worker loop can still read/write to the modified tables.

## 📤 Output Format

```text
MIGRATION_ID: [revision_hash]
BACKUP_STATUS: [CONFIRMED]
SCHEMA_CHANGE: [Brief description]
VALIDATION_RESULT: [PASS | FAIL]

---
CURRENT_STAGE: L1-Migrate
RECOMMENDED_NEXT: /jadzia-test
---
```
