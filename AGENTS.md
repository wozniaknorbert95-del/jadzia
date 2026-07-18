# Agent rules — Jadzia Core / FlexGrafik

## Canonical knowledge

- **Canonical brain**: `brain.md` (this repo)
- **Canonical backlog**: `todo.json` (this repo)
- **Active program**: FlexGrafik AI OS — closeout loop (`standing_go_closeout`)
- **Active plan / gate**: `active_gate` = head of `closeout_queue` (start: `COI-PM-01`)
- **Latest handoff**: `docs/handoffs/2026-07-18-coi-ops-ai-01-CLOSE.md`
- **Scorecard (surowy)**: `docs/ops/SCORECARD-AI-OS-ZALICZENIE.md` — #1–4,6,7,9 LIVE; #5/#8 PARTIAL until closeout
- **Post-coding**: `.agents/workflows/post-coding.md` (L3.5 drain)
- **AI MBA spine**: `docs/learning/AI-MBA-FLEXGRAFIK-SPINE.md` (spine only)
- **Knowledge index**: `docs/ops/KNOWLEDGE-SYSTEM-INDEX.md` (+ meta/VCMS mirrors COI-KNOW-01)
- **Phone hub ADR**: `docs/design/coi-commander/adr/D0.6-phone-hub-not-merge.md` (+ D0.15)
- **Prod tip SoT:** VPS `/opt/jadzia` `git rev-parse --short HEAD`
- **Deploy runbook**: `.agents/workflows/jadzia-deploy.md` (+ `deployment/rev-demand-01-deploy-vps.sh`)
- **Module spec (COI)**: `flexgrafik-meta/docs/core/modules/module-jadzia-core.md`

## Guardrails

- **No-ask (Dowódca):** one path, execute; park human-only as `ready_for_human`.
- **Zasada 11:** VPS OK when `standing_go_closeout` or GO in-session; else COMMAND_BLOCK only.
- **Hard STOP:** Gate D, Mollie LIVE, secret rotation, merge OS↔jadzia, fake PASS.
- **Least privilege**: no secrets / large binaries / `_mint_*` / `_recover_*`.
- **1-1-1** per `/post-coding` gate; handoff required.
- **Honesty:** no PASS/completed without dogfood number or URL.
- **Closeout expires:** `2026-07-25` → then `standing_go_closeout` must be false unless new GO.

## Copy & languages

- Internal coordination can be PL.
- User-facing UI copy follows target module language rules.
