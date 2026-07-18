# Agent rules — Jadzia Core / FlexGrafik

## Canonical knowledge

- **Canonical brain**: `brain.md` (this repo)
- **Canonical backlog**: `todo.json` (this repo)
- **Active program**: FlexGrafik AI OS LIVE; **MBA Agent YEAR CLOSE** (weeks W08–W52)
- **Active plan / gate**: none — Dowódca PASS / Year zaliczenie = human; next feature poza MBA
- **Latest handoff**: `docs/handoffs/2026-07-18-session-CLOSE-mba-YEAR-agent.md`
- **Scorecard**: `docs/ops/SCORECARD-AI-OS-ZALICZENIE.md` — **#1–9 LIVE**
- **MBA spine**: `docs/learning/AI-MBA-FLEXGRAFIK-SPINE.md` (+ `weeks/W08`–`W52`)
- **Post-coding**: `.agents/workflows/post-coding.md` (fresh GO for VPS)
- **Knowledge / processes**: `docs/ops/KNOWLEDGE-SYSTEM-INDEX.md`, `PROCESS-CATALOG.md`
- **Prod tip SoT:** VPS `/opt/jadzia` `git rev-parse --short HEAD`
- **Deploy**: `.agents/workflows/jadzia-deploy.md`

## Guardrails

- **No-ask:** one path, execute; park human-only as `ready_for_human`.
- **Zasada 11:** VPS only with GO (`standing_go_closeout` **false**).
- **Hard STOP:** Gate D, Mollie LIVE, secrets, merge OS↔jadzia, fake PASS.
- **MBA:** nie regeneruj W08–W52; nie zaznaczaj kolumny Dowódca.
- **Least privilege:** no `_mint_*` / `_recover_*` in commits.

## Copy & languages

- Internal coordination can be PL.
- User-facing UI copy follows target module language rules.
