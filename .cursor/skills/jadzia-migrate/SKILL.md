---
name: jadzia-migrate
description: >-
  Alembic/DB schema change procedure for jadzia-core. Use when schema or jadzia.db structure changes.
disable-model-invocation: true
---

# /jadzia-migrate

## Goal

Bezpieczna migracja schematu SQLite z backupem i dokumentacją PRD.

## Canonical workflow

- **[.agents/workflows/jadzia-migrate.md](../../.agents/workflows/jadzia-migrate.md)**

## Don't

- Run `alembic upgrade` on production VPS autonomously
- Change schema without PRD/schema doc update

## Output

```text
MIGRATION: [revision id | new migration name]
BACKUP: [local path | VPS Commander step]
PRD_UPDATED: [yes|no]

---
CURRENT_STAGE: F3-Implement
RECOMMENDED_NEXT: [/jadzia-test | /implement]
WHY_NEXT: [...]
---
```
