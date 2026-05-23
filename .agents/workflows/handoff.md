---
description: Handoff jadzia-core — plik docs/handoffs + todo.json + CORE NEXT_COMMAND.
---

# /handoff

## Goal

State transfer: plik handoff + aktualizacja `todo.json` + blok CORE dla następnej sesji.

## Procedure

1. `git branch --show-current`, `git status -sb`, `git log -1 --oneline`
2. Write `docs/handoffs/YYYY-MM-DD-[slug].md`
3. Update `todo.json` — `last_updated`, task status
4. Emit CORE block: DONE/LEFT/RISKS/V-FILES/NEXT_COMMAND_FOR_NEW_AGENT
5. Commit **tylko na prośbę** Dowódcy

## NEXT_COMMAND router

| Situation | NEXT_COMMAND |
|-----------|--------------|
| Unclear scope | `@vibe-init` + V-FILES |
| Feature, no BLAST | `@blast` + todo id |
| Feature, BLAST exists | `@implement` + anchor path |
| Bug unknown | `@debug` |
| Schema | `@jadzia-migrate` |
| Deploy-ready | `@jadzia-deploy` — see [jadzia-deploy.md](jadzia-deploy.md) |
| After deploy | `@handoff` or close |
