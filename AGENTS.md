# Agent rules — Jadzia Core / FlexGrafik

## Canonical knowledge

- **Canonical brain**: `brain.md` (this repo)
- **Canonical backlog**: `todo.json` (this repo)
- **Active program**: MOBILE-02 LIVE; Demand F0–F7 + MOBILE-01 LIVE (`87d7912`)
- **Active plan / gate**: `todo.json` → `active_gate` = `NONE` (await next GO)
- **Latest handoff**: `docs/handoffs/2026-07-18-coi-cmd-mobile-02-CLOSE.md`
- **Phone hub ADR**: `docs/design/coi-commander/adr/D0.6-phone-hub-not-merge.md`
- **Prod tip SoT:** VPS `/opt/jadzia` `git rev-parse --short HEAD` (MOBILE-02 LIVE **`81347e8`**, FEATURE `abba339`). Do not tip-chase every docs commit; FEATURE_SHA stays in task notes.
- **Deploy runbook**: `docs/ops/INT-002-V2-DEPLOY.md` (+ `deployment/rev-demand-01-deploy-vps.sh`)
- **Reconciliation runbook**: `docs/ops/REVENUE-RECONCILIATION.md`
- **Approved contract**: `docs/contracts/REVENUE-EVENT-CONTRACT-v1.md`
- **Module spec (COI)**: `flexgrafik-meta/docs/core/modules/module-jadzia-core.md`
- **COI charter**: `flexgrafik-meta/docs/core/jadzia-operating-charter.md`
- **Integration contracts**: `flexgrafik-meta/docs/core/integration-contracts.md`
- **Global rules** (system-wide): `flex-vcms/docs/core/global-rules.md`
- **Workflow** (system-wide): `flexgrafik-meta/docs/core/workflow-manual.md`

## Guardrails

- **No-ask (Dowódca):** Never ask clarifying A/B/C questions. Recommend one path, justify briefly, decide and execute (or park human-only blockers with a checklist). See `.cursor/rules/dowodca-no-ask.mdc`.
- **Manual deploy only** (Zasada 11) unless Dowódca explicitly authorizes in-session.
- **Least privilege**: do not read or process secrets (`.env*`, keys) or large binaries.
- **1-1-1 rule**: implement one change at a time; finish with a handoff note in `docs/handoffs/`.
- **REV deploy order**: integrate REV-R0-02A → deploy Jadzia INT-002 v2 consumer → deploy zzpackage producer → controlled E2E.
- **Current prod state**: Jadzia VPS **`master`** (verified tip **`7aa32d8`**, FEATURE UI `87d7912`, Demand-03 FEATURE `367549f`); producer theme `@ bfe8485`; Gate C PASS (#3209); COD OFF; iDEAL-only; Mollie TEST; **Gate D parked**; min 199 unchanged.

## Copy & languages

- Internal coordination can be PL.
- Any user-facing UI copy must follow the product language rules of the target module.
