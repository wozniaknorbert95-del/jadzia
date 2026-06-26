---
name: vibe-init
description: >-
  Starts jadzia-core session: classify task, load rules, CORE route to /blast or /debug.
  Use at session start, after /handoff, or after /context-reset.
disable-model-invocation: true
---

# /vibe-init

## Goal

Mapowanie sytuacji, wczytanie zasad modułu AI i wybór ścieżki (Standard vs Fast-Track).

## When to use

- **`/vibe-init`**
- After **`/handoff`** or **`/context-reset`** in new chat
- Commander ticket at session start

## Canonical workflow

- **[.agents/workflows/vibe-init.md](../../.agents/workflows/vibe-init.md)**

## Input

Problem/Ticket od Dowódcy; optional handoff `V-FILES` (max 4).

## Do

- [.agents/workflows/implement.md](../../.agents/workflows/implement.md) when **Hotfix**
- [AGENTS.md](../../AGENTS.md), [brain.md](../../brain.md), [todo.json](../../todo.json)
- [docs/PRD-core.md](../../docs/PRD-core.md) for VPS/service context
- global-rules from flexgrafik-meta if in workspace

## Don't

- Deep architecture on Hotfix/service restart
- Require `/debug` when cause is in ticket
- Autonomous deploy (Zasada 11)
- Read `.env*` or secrets

## Task classification router

| Signals | TASK_CLASSIFICATION | RECOMMENDED_NEXT |
|---------|---------------------|------------------|
| New node, API, LangGraph flow | **Feature** | **`/blast`** |
| Bug, 500, webhook fail, unknown | **Bugfix** | **`/debug`** |
| Known cause, narrow Python fix | **Hotfix** | `/implement` |
| Schema / alembic change | **Migrate** | **`/migrate`** |
| Ship to VPS production | **Deploy** | `/jadzia-test` → `/audit-red-team` → `/jadzia-deploy` |

## Output

```text
TASK_CLASSIFICATION: [Feature/Bugfix/Hotfix/Migrate/Deploy]
CONSTRAINTS: [...]
RISKS: [...]
MISSING: [NONE|...]
READY: [YES|NO]

---
CURRENT_STAGE: F1-Plan
RECOMMENDED_NEXT: [/blast | /blueprint | /debug | /implement | /migrate | /jadzia-test | /audit-red-team | /jadzia-deploy]
WHY_NEXT: [...]
---
```

## Done when

One CORE `RECOMMENDED_NEXT` printed — no premature implementation.
