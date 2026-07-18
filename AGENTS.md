# Agent rules — Jadzia Core / FlexGrafik

## Canonical knowledge

- **Canonical brain**: `brain.md` (this repo)
- **Canonical backlog**: `todo.json` (this repo)
- **Active program**: FlexGrafik AI OS — Dashboard + CS + Knowledge LIVE; reszta surowa
- **Active plan / gate**: `active_gate` = `COI-OPS-AI-01` (45.8% FAIL)
- **Latest handoff**: `docs/handoffs/2026-07-18-coi-know-01-CLOSE.md`
- **Scorecard (surowy)**: `docs/ops/SCORECARD-AI-OS-ZALICZENIE.md` — Dashboard+CS+Wiedza **LIVE**; PM/PROC PARTIAL; OPS-AI **45.8% FAIL**
- **AI MBA spine**: `docs/learning/AI-MBA-FLEXGRAFIK-SPINE.md` (spine only)
- **Knowledge index**: `docs/ops/KNOWLEDGE-SYSTEM-INDEX.md` (+ meta/VCMS mirrors COI-KNOW-01)
- **Phone hub ADR**: `docs/design/coi-commander/adr/D0.6-phone-hub-not-merge.md` (+ D0.15)
- **Prod tip SoT:** VPS `/opt/jadzia` `git rev-parse --short HEAD`
- **Deploy runbook**: `docs/ops/INT-002-V2-DEPLOY.md` (+ `deployment/rev-demand-01-deploy-vps.sh`)
- **Module spec (COI)**: `flexgrafik-meta/docs/core/modules/module-jadzia-core.md`

## Guardrails

- **No-ask (Dowódca):** Recommend one path, decide, execute; park human-only as `ready_for_human`.
- **Manual deploy only** (Zasada 11) unless GO in-session.
- **Least privilege**: no secrets / large binaries.
- **1-1-1**: one gate per session; handoff required.
- **Honesty:** nie oznaczać PASS/completed bez dogfood lub liczby (OPS-AI).
- **Current:** KNOW-01 mirrors LIVE; OPS-AI-01 `in_progress` @ 45.8%; Gate D parked.

## Copy & languages

- Internal coordination can be PL.
- User-facing UI copy follows target module language rules.
