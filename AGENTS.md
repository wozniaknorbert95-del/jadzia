# Agent rules — Jadzia Core / FlexGrafik

## Ops (LIVE)

- **Operator playbook**: `docs/ops/JADZIA-OPERATOR-PLAYBOOK.md`
- **Knowledge SoT**: `docs/ops/KNOWLEDGE-SYSTEM-INDEX.md` (COI-KNOW-02 DONE)
- **Process catalog**: `docs/ops/PROCESS-CATALOG.md`
- **Scorecard**: `docs/ops/SCORECARD-AI-OS-ZALICZENIE.md` — **#1–9 LIVE**
- **Canonical brain**: `brain.md` · **backlog**: `todo.json`
- **Prod tip SoT:** VPS `/opt/jadzia` `git rev-parse --short HEAD`
- **Deploy**: `.agents/workflows/jadzia-deploy.md`
- **Post-coding**: `.agents/workflows/post-coding.md` (fresh GO for VPS)
- **Latest handoffs**: `docs/handoffs/` (≤15 rolling; MBA archived)

## MBA

**COMPLETE** (W00–W52) — nie regeneruj tygodni; nie zaznaczaj kolumny Dowódca.

## Guardrails

- **No-ask:** one path, execute; park human-only as `ready_for_human`.
- **Zasada 11:** VPS only with GO (`standing_go_closeout` **false**).
- **Hard STOP:** Gate D, Mollie LIVE, secrets, merge OS↔jadzia, fake PASS.
- **Least privilege:** no `_mint_*` / `_recover_*` in commits (gitignored).

## Copy & languages

- Internal coordination can be PL.
- User-facing UI copy follows target module language rules.
