# Agent rules — Jadzia Core / FlexGrafik

## Ops (LIVE)

- **Operator playbook**: `docs/ops/JADZIA-OPERATOR-PLAYBOOK.md`
- **Knowledge SoT**: `docs/ops/KNOWLEDGE-SYSTEM-INDEX.md` (ECO-POLISH-01 CLOSE — Docs IA policy)
- **Process catalog**: `docs/ops/PROCESS-CATALOG.md`
- **Scorecard**: `docs/ops/SCORECARD-AI-OS-ZALICZENIE.md` — **#1–9 LIVE**
- **VHQ Program (ACTIVE)**: `docs/ops/FLEXGRAFIK-VIRTUAL-HQ-PROGRAM.md`
- **Campus Program**: SUPERSEDED — `docs/ops/FLEXGRAFIK-CAMPUS-PROGRAM.md` (foundation only)
- **VHQ Decision Instrument scorecard**: `docs/ops/VHQ-DECISION-INSTRUMENT-SCORECARD.md` · workflow `/vhq-decision-instrument` (agent closeout DONE; S7 parked)
- **Lanes appendix**: `docs/ops/PROGRAM-LANES-SOT.md` (not `todo.plan`)
- **Canonical brain**: `brain.md` · **backlog / active_gate**: `todo.json`
- **Prod tip SoT:** VPS `/opt/jadzia` `git rev-parse --short HEAD`
- **Deploy**: `.agents/workflows/jadzia-deploy.md`
- **Post-coding**: `.agents/workflows/post-coding.md` (fresh GO for VPS)
- **Latest handoffs**: `docs/handoffs/` (≤15 rolling; MBA archived)
- **Marketing OS**: fazy = `PROGRAM-PHASES.md` · **Etap 4 OPS HARDENING SEALED** · prod `a3deb59` · live P0 **PARKED** · unlock = `UNLOCK-LIVE-P0.md`

## MBA

**COMPLETE** (W00–W52) — nie regeneruj tygodni; nie zaznaczaj kolumny Dowódca.

## Guardrails

- **No-ask:** one path, execute; park human-only as `ready_for_human`.
- **Zasada 11:** VPS only with GO (`standing_go_closeout` **false**).
- **Hard STOP:** Gate D, Mollie LIVE, secrets, merge OS↔jadzia, fake PASS.
- **Demand OS TOOL FIRST:** najpierw narzędzie 100%; publikacje tylko testowo (publish→delete); live `4-P0-*` dopiero po jawnym unlock Dowódcy. Rule: `.cursor/rules/demand-os-tool-first.mdc`.
- **Least privilege:** no `_mint_*` / `_recover_*` in commits (gitignored).

## Copy & languages

- Internal coordination can be PL.
- User-facing UI copy follows target module language rules.
