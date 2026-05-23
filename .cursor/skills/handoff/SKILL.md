---
name: handoff
description: >-
  Ends session: docs/handoffs file, todo.json update, CORE V-FILES and NEXT_COMMAND.
  Use when /handoff, context full, or after deploy milestone.
disable-model-invocation: true
---

# /handoff

## Goal

State transfer — plik w `docs/handoffs/`, `todo.json`, blok CORE dla następnej sesji.

## Canonical workflow

- **[.agents/workflows/handoff.md](../../.agents/workflows/handoff.md)**

## When to use

- **`/handoff`**, end session, after deploy, context limit

## Agent procedure

1. Gather git state (branch, status, log-1).
2. Write `docs/handoffs/YYYY-MM-DD-[slug].md`.
3. Update **`todo.json`** — `last_updated`, task status.
4. Emit **CORE chat block** (required).
5. Commit/push **only if user asks**.

## CORE chat block (required)

```text
DONE: [...]
LEFT: [...]
RISKS: [...]
V-FILES: [1-4 absolute paths]
NEXT_COMMAND_FOR_NEW_AGENT: [@vibe-init | @blast | @debug | @jadzia-deploy + checklist]

---
CURRENT_STAGE: F6-Iterate
RECOMMENDED_NEXT: (new session uses NEXT_COMMAND)
WHY_NEXT: State preserved outside chat
---
```

## NEXT_COMMAND router

| Situation | NEXT_COMMAND |
|-----------|--------------|
| Unclear scope | `@vibe-init` + V-FILES |
| Feature, no BLAST | `@blast` + todo id |
| BLAST exists | `@implement` + anchor |
| Bug unknown | `@debug` |
| Schema change | `@jadzia-migrate` |
| Pre-deploy | `@jadzia-test` → `@audit-red-team` |
| Deploy-ready | `@jadzia-deploy` — Commander executes VPS |
| After deploy | `@handoff` or close |

## Don't

- Handoff only in chat without file
- Invent deploy results
- Mark todo DONE without reality match
