# Agent rules — Jadzia Core / FlexGrafik

## Canonical knowledge

- **Canonical brain**: `brain.md` (this repo)
- **Canonical backlog**: `todo.json` (this repo)
- **Active program**: REV-DEMAND Demand Engine (01 COMPLETE; next 02 session durability; Gate D parked)
- **Active plan / gate**: `todo.json` → `active_gate` = `REV-DEMAND-02`
- **Latest handoff**: `docs/handoffs/2026-07-18-rev-demand-01-CLOSE.md`
- **Dogfood playbook**: `docs/ops/JADZIA-REVENUE-DOGFOOD.md`
- **Deploy runbook**: `docs/ops/INT-002-V2-DEPLOY.md`
- **Reconciliation runbook**: `docs/ops/REVENUE-RECONCILIATION.md`
- **Approved contract**: `docs/contracts/REVENUE-EVENT-CONTRACT-v1.md`
- **Module spec (COI)**: `flexgrafik-meta/docs/core/modules/module-jadzia-core.md`
- **COI charter**: `flexgrafik-meta/docs/core/jadzia-operating-charter.md`
- **Integration contracts**: `flexgrafik-meta/docs/core/integration-contracts.md`
- **Global rules** (system-wide): `flex-vcms/docs/core/global-rules.md`
- **Workflow** (system-wide): `flexgrafik-meta/docs/core/workflow-manual.md`

## Guardrails

- **No-ask (Dowódca):** Never ask clarifying A/B/C questions. Recommend one path, justify briefly, decide and execute (or park human-only blockers with a checklist). See `.cursor/rules/dowodca-no-ask.mdc`.
- **Manual deploy only** (Zasada 11). Agents may prepare commands and checklists, but do not deploy autonomously.
- **Least privilege**: do not read or process secrets (`.env*`, keys) or large binaries.
- **1-1-1 rule**: implement one change at a time; finish with a handoff note in `docs/handoffs/`.
- **REV deploy order**: integrate REV-R0-02A → deploy Jadzia INT-002 v2 consumer → deploy zzpackage producer → controlled E2E.
- **Current prod state**: consumer @ `504fdf6` and producer @ `bfe8485` deployed; Gate C PASS (WC#3209 test); COD OFF; checkout iDEAL-only; Mollie still TEST; **Gate D parked** (no top-up); min checkout 199 unchanged.

## Copy & languages

- Internal coordination can be PL.
- Any user-facing UI copy must follow the product language rules of the target module.
