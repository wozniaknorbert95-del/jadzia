# Context Anchor / Project-Instructions (V4)

## READ FIRST

- `../flexgrafik-meta/docs/core/workflow-manual.md`
- `../flexgrafik-meta/docs/core/global-rules.md`
- `../flexgrafik-meta/docs/core/agents.md`
- `../flexgrafik-meta/docs/core/modules/module-jadzia-core.md`
- `../flexgrafik-meta/docs/core/jadzia-operating-charter.md`
- `brain.md` (this repo)

## GOAL

Develop and maintain **Jadzia COI backend** for FlexGrafik: Python + FastAPI + custom node pipeline + SQLite on VPS (`185.243.54.115`). Follow workflow-manual.md and global-rules.md.

**AS-IS:** WP SSH agent, Wizard widget, worker/HITL queue (~40% of COI vision).
**TO-BE Phase A:** `order_node` + WooCommerce webhook (INT-002).

## CONSTRAINTS

- Work on feature branch when possible; pre-commit hook must pass before push.
- Do not modify files outside your scope (respect `api/`, `core/`, `agent/` boundaries).
- Schema/PRD changes before code changes.
- Manual deploy only (Zasada 11).

## SESSION START

1. Run `/vibe-init` — load `todo.json`, `brain.md`, module spec.
2. Follow `RECOMMENDED_NEXT` from triage.
3. Close with `/handoff` in `docs/handoffs/`.
