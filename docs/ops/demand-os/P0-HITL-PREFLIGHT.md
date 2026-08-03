---
status: PARKED
updated: "2026-08-03"
gate: DEMAND-OS-MARKETING-4-00
owner: agent-orchestrator
active: 4-TOOL-01
note: "live P0 parked — tool 100% first"
---

# Etap 4 P0 — HITL Preflight Pack

## Scope

Ten pakiet przygotowuje wejście w:

- `4-P0-01` TT publish `tt_w32_install_01`
- `4-P0-02` FB hunt comment #1
- `4-P0-03` blog ship `blog_w31_install_bus50m`

## Inputs

- TT caption: `docs/ops/demand-os/set-now/cap_tt_w32_01.txt`
- FB hunt checklist: `docs/ops/demand-os/set-now/FB-HUNT-DAILY.md`
- Blog draft MD: `docs/ops/demand-os/set-now/BLOG-DRAFTS/blog_w31_install_bus50m.md`
- Blog draft JSON: `docs/ops/demand-os/set-now/BLOG-DRAFTS/blog_w31_install_bus50m.json`
- Ledger target: `docs/ops/demand-os/set-now/LEDGER.csv`

## Hard gates

1. `python tools/demand_os_hub.py doctor` = `ok: true`
2. `python -m pytest tests -k demand_os -q` = green
3. Asset has Validator PASS / gate ALLOW before any human publish
4. Execution is HITL-only; no autonomous publish from branch
5. Ads remain parked

## P0 sequence

1. Verify TT asset `tt_w32_install_01` is still gate-allowed.
2. Review caption against current ICP / CTA.
3. Review FB hunt target and one-comment rule.
4. Review blog draft against same single CTA path.
5. Prepare ledger row template before any live action.
6. Hand off to human HITL execution.

## STOP

- No VPS deploy
- No autonomous TT / FB / blog publish
- No Ads / boost / paid spend
- No fake ledger evidence
