---
description: BLAST plan — anchor przed implementacją jadzia-core.
---

# /blast

## Goal

Trwały kontrakt techniczny przed edycją modułu Python (FastAPI, LangGraph, nodes).

## Procedure

1. **B** Background — endpoint/node, integracja (Telegram, webhook, SSH), backlog id z `todo.json`.
2. **L** Limitations — VPS service, SQLite locks, alembic, least privilege SSH, rate limits.
3. **A** Actions — `[ ]` checklist (files, tests, docs).
4. **S** Success — binary Pass/Fail (pytest + `/health` smoke).
5. **T** Tests — `pytest` scope; manual Telegram/webhook if touched.
6. Anchor: `.cursor/current-task.md` or `docs/handoffs/YYYY-MM-DD-*-blast.md`.
7. Wait for Commander approval.

## Output

```text
BLAST_ANCHOR: [path]
BACKLOG_ID: [todo.json task id | NONE]
DOD: [...]

---
CURRENT_STAGE: F2-Design
RECOMMENDED_NEXT: /implement (after approval)
WHY_NEXT: Plan anchored
---
```
