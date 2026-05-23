---
description: Alembic / schema migration — backup + PRD + test gate.
---

# /jadzia-migrate

## Goal

Controlled DB schema change for `jadzia.db` with rollback path.

## Procedure

1. Document change in module docs / `docs/PRD-core.md` schema section.
2. Create or review alembic revision locally.
3. **Backup:** local copy of DB; VPS: Commander runs backup per [PRD-core.md](../../docs/PRD-core.md) deploy flow step 2.
4. Run `alembic upgrade head` locally; verify with tests.
5. Never deploy migration to VPS without `/jadzia-test` green + Commander approval.

## Do

- One migration per session (1-1-1)
- Rollback plan: `alembic downgrade -1` + DB restore

## Don't

- Autonomous VPS migration
- Skip backup on production path

## Output

```text
MIGRATION: [revision]
BACKUP: [path or Commander checklist item]
PRD_UPDATED: [yes|no]

---
CURRENT_STAGE: F3-Implement
RECOMMENDED_NEXT: [/jadzia-test]
WHY_NEXT: Verify migration before deploy
---
```
