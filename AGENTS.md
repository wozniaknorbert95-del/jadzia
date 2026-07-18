# Agent rules — Jadzia Core / FlexGrafik

## Canonical knowledge

- **Canonical brain**: `brain.md` (this repo)
- **Canonical backlog**: `todo.json` (this repo)
- **Active program**: FlexGrafik AI OS — **zaliczenie LIVE** (CLOSEOUT 2026-07-18)
- **Active plan / gate**: none (`active_gate` null; maintain)
- **Latest handoff**: `docs/handoffs/2026-07-18-ai-os-CLOSEOUT.md`
- **Scorecard**: `docs/ops/SCORECARD-AI-OS-ZALICZENIE.md` — **#1–9 LIVE**
- **Post-coding**: `.agents/workflows/post-coding.md` (L3.5; use with fresh GO)
- **AI MBA spine**: `docs/learning/AI-MBA-FLEXGRAFIK-SPINE.md`
- **Knowledge index**: `docs/ops/KNOWLEDGE-SYSTEM-INDEX.md`
- **Process catalog**: `docs/ops/PROCESS-CATALOG.md` (+ VCMS/meta PROC-02)
- **Phone hub ADR**: `docs/design/coi-commander/adr/D0.6-phone-hub-not-merge.md`
- **Prod tip SoT:** VPS `/opt/jadzia` `git rev-parse --short HEAD`
- **Deploy**: `.agents/workflows/jadzia-deploy.md` (+ `deployment/rev-demand-01-deploy-vps.sh`)
- **Module spec**: `flexgrafik-meta/docs/core/modules/module-jadzia-core.md`

## Guardrails

- **No-ask:** one path, execute; park human-only as `ready_for_human`.
- **Zasada 11:** VPS only with GO in-session (`standing_go_closeout` currently **false**).
- **Hard STOP:** Gate D, Mollie LIVE, secret rotation, merge OS↔jadzia, fake PASS.
- **Least privilege:** no secrets / `_mint_*` / `_recover_*`.
- **1-1-1** + `/post-coding` + handoff.
- **Honesty:** no PASS without evidence.

## Copy & languages

- Internal coordination can be PL.
- User-facing UI copy follows target module language rules.
