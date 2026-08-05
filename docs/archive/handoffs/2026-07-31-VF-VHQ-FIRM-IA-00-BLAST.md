---
status: "[BLAST]"
title: "VF-VHQ-FIRM-IA-00 — Firm map IA + single shell"
updated: "2026-07-31"
gate: "VF-VHQ-FIRM-IA-00"
spec: "docs/superpowers/specs/2026-07-31-vhq-firm-ia-design.md"
plan: "docs/superpowers/plans/2026-07-31-vhq-firm-ia.md"
prod_baseline: "ebe38db / runtime 2623ae2 / cache vhq-w65a"
cache_target: "vhq-w66a"
runtime_changes_allowed: true
founder_go: "Spec approved 2026-07-31 (brainstorm)"
---

# BLAST — VF-VHQ-FIRM-IA-00

## Intent (1-1-1)

Make Virtual HQ feel like **one company in one home** — Firm Chain IA (Demand → Sell → Deliver → Direct) + Console demoted from Esc parent — without building Order Desk or touching DI logic.

Priority: **A** maintain DI · **B** firm IA (this gate) · **C** Order Desk out of scope.

## Binary DoD (spec §2 + §6)

| # | DoD | Pass when |
|---|-----|-----------|
| D1 | One home | Cold open → HQ › Mission Control |
| D2 | One company story | Firm Chain strip always visible; Demand→Sell→Deliver→Direct narratable in ≤30s |
| D3 | Console = tools | Esc: room → MC → **stay in HQ** (no Console parent); Tools/Sign-in opens Console; Return to HQ works |
| D4 | Honest PARKED | Order Desk + deliver rooms show role + status + unlock (EV-W2-010); **no LIVE KPI** |
| D5 | DI regression | NBA / money-risk / Vault still present on MC; Q3/Q6 readable after deploy |
| D6 | Local dogfood | Spec §6 local checklist all PASS before PRECLOSE |
| D7 | Prod dogfood | Same checklist on `?v=vhq-w66a` after Founder `GO DEPLOY` |
| D8 | Contract tests | `test_vhq_firm_ia_contracts.py` green |

## Work packages (order)

1. **WP-A Shell primacy (D)** — Esc ladder, `#vhq-to-console` / `#vhq-close` labels, `.vhq-shell__hint`; Console ≠ HQ parent  
2. **WP-B Firm IA (B)** — `firmStage` on `VHQ_ROOMS`, Firm Chain strip, floor band relabel, PARKED role/unlock copy  
3. **WP-C Regression** — DI surfaces + EV-W2-010 preserved + local dogfood; deploy pack; **no deploy without GO**

Each WP: implement → local verify → commit. Single deploy after WP-C.

## Scope

| Path | Change |
|------|--------|
| `commander-ui/app.js` | Esc ladder, `VHQ_ROOMS` +`firmStage`/`firmRole`/`unlockHint`, Firm Chain JS |
| `commander-ui/index.html` | CTA labels, hint, eyebrow, Firm Chain markup, floor titles, `?v=` |
| `commander-ui/styles.css` | Firm Chain strip + stage highlight |
| `commander-ui/sw.js` | `CACHE = coi-commander-shell-vhq-w66a` |
| `tests/unit/test_vhq_firm_ia_contracts.py` | Esc/Console/firmStage/EV-W2-010 string contracts |
| `todo.json` + ops tips | Gate closeout + tip sync (Task 6) |

No new Python routes. Floor IDs `P0–P3` unchanged.

## STOP

- Order Desk LIVE / S7 fake PASS / inventing fulfilment SoT (**preserve EV-W2-010**)
- 3D unpark · Ads · Mollie · Gate D
- 6th Commander tab
- New backend APIs / Ops Bus catalog expansion
- Mass room migration across `P0–P3` IDs in v1
- Reopening DI scorecard gates S3–S6/S8
- Staging `docs/ops/marketing/MKT/**` or ASSET-MATERIALS-PREP
- Deploy without explicit Founder `GO DEPLOY`

## Validate

```bash
pytest tests/unit/test_vhq_firm_ia_contracts.py tests/unit/test_commander_money_narrative.py tests/unit/test_commander_nba.py -v
```

Local dogfood: spec §6 checklist. Prod: same after GO + cache `vhq-w66a`.

## Exit

PRECLOSE → local dogfood evidence → CLOSE → deploy pack → prod verify → `active_gate: null` / `firm_ia_done_idle`.
