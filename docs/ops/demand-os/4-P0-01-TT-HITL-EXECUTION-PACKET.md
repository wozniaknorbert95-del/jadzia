---
status: PARKED
updated: "2026-08-03"
gate: DEMAND-OS-MARKETING-4-00
asset_id: tt_w32_install_01
mode: HITL-only · live PARKED · test-only if tool needs proof
---

# 4-P0-01 — TT HITL Execution Packet

## Decision

`4-P0-01` **live is PARKED**. Dowódca direction 2026-08-03: **tool 100% first**.  
Any publish allowed only as **test → delete** for tool proof — not live P0 SEAL.

## Evidence (session 2026-08-03)

- `python tools/demand_os_hub.py doctor` → `ok: true` · `marketing: HITL_LIVE`
- `go_day_ready` → `score: 100.0` · `ok: true`
- local `marketing_hitl_gate` → `BLOCKED` (no local env GO; prod remains READY per EXEC-CLOSE)
- `python -m pytest tests -k demand_os -q` → `102 passed`
- `python tools/demand_os_f2.py gate --asset-id tt_w32_install_01` → `GATE ALLOW`
- Caption CTA: Wizard-only UTM `tt_w32_install_01` (single CTA confirmed)

## Primary asset

- Caption: `docs/ops/demand-os/set-now/cap_tt_w32_01.txt`
- Asset id: `tt_w32_install_01`
- CTA path: Wizard only

## Supporting assets

- FB hunt playbook: `docs/ops/demand-os/set-now/FB-HUNT-DAILY.md`
- Blog draft: `docs/ops/demand-os/set-now/BLOG-DRAFTS/blog_w31_install_bus50m.md`
- Ledger target: `docs/ops/demand-os/set-now/LEDGER.csv`

## HITL operator flow

1. Re-read TT caption and confirm one CTA only.
2. Confirm `GATE ALLOW` for `tt_w32_install_01`.
3. Publish via human HITL path only.
4. Append ledger evidence after publish.
5. Keep FB hunt and blog as next, not same-step bundling.

## Guardrails

- No Ads / boost / paid
- No VPS deploy
- No autonomous social publish
- No fake ledger row
- No second CTA path beside Wizard
