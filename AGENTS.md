# Agent rules — Jadzia Core / FlexGrafik

## Canonical knowledge

- **Canonical brain**: `brain.md` (this repo)
- **Canonical backlog**: `todo.json` (this repo)
- **Active plan / gate**: `todo.json` → `active_gate` = `COI-CMD-SMTP-01` (M2 video LIVE; session closed 2026-07-17)
- **Latest handoff**: `docs/handoffs/2026-07-17-session-close-M2-SMTP-next.md`
- **Module spec (COI)**: `flexgrafik-meta/docs/core/modules/module-jadzia-core.md`
- **COI charter**: `flexgrafik-meta/docs/core/jadzia-operating-charter.md`
- **Integration contracts**: `flexgrafik-meta/docs/core/integration-contracts.md`
- **Global rules** (system-wide): `flex-vcms/docs/core/global-rules.md`
- **Workflow** (system-wide): `flexgrafik-meta/docs/core/workflow-manual.md`

## Guardrails

- **Manual deploy only** (Zasada 11). Agents may prepare commands and checklists, but do not deploy autonomously.
- **Least privilege**: do not read or process secrets (`.env*`, keys) or large binaries.
- **1-1-1 rule**: implement one change at a time; finish with a handoff note in `docs/handoffs/`.

## Copy & languages

- Internal coordination can be PL.
- Any user-facing UI copy must follow the product language rules of the target module.
