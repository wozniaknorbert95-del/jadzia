---
description: Start sesji jadzia-core. CORE router F1-Plan.
---

# /vibe-init

## Goal

Mapowanie sytuacji, wczytanie zasad i wybór ścieżki (Standard vs Fast-Track).

## Input

Problem/Ticket; optional handoff `V-FILES` (max 4).

## Agent procedure

1. Skim **[AGENTS.md](../../AGENTS.md)**, **[brain.md](../../brain.md)**, **[todo.json](../../todo.json)**.
2. **Deploy/Hotfix:** [pre-flight.md](pre-flight.md) — skip deep architecture.
3. Classify; emit Output.

## Task classification router

| Signals | TASK_CLASSIFICATION | RECOMMENDED_NEXT |
|---------|---------------------|------------------|
| New node, API endpoint, LangGraph | **Feature** | **`/blast`** |
| Bug, regression, unknown cause | **Bugfix** | **`/debug`** |
| Known cause, narrow fix, urgency | **Hotfix** | `/pre-flight` → implement |
| DB schema / alembic | **Migrate** | **`/jadzia-migrate`** |
| Ship commits to VPS | **Deploy** | `/pre-flight` → `/jadzia-test` → `/audit-red-team` → `/jadzia-deploy` |

## Output

```text
TASK_CLASSIFICATION: [Feature/Bugfix/Hotfix/Migrate/Deploy]
CONSTRAINTS: [...]
RISKS: [...]
MISSING: [NONE|...]
READY: [YES|NO]

---
CURRENT_STAGE: F1-Plan
RECOMMENDED_NEXT: [/blast | /debug | /pre-flight | /jadzia-migrate | /jadzia-test | /audit-red-team | /jadzia-deploy]
WHY_NEXT: [...]
---
```
