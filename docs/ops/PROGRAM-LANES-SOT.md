---
status: "[APPENDIX]"
title: "Program lanes — DONE vs WAITING (ściąga, nie plan)"
updated: "2026-07-31"
owner: "Dowódca + agent"
tip: "COM-AI-50-SHIP DEPLOY PASS · tip fcf6a9f · VHQ cache vhq-w68a"
cache: "vhq-w68a"
parent_program: "docs/ops/FLEXGRAFIK-VIRTUAL-HQ-PROGRAM.md"
todo: "todo.json"
scorecard: "docs/ops/VHQ-DECISION-INSTRUMENT-SCORECARD.md"
order_desk_sot: "docs/ops/ORDER-DESK-SOT-v0.md"
---

# Program lanes — ściąga DONE / WAITING

**Prod VHQ:** https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w68a  
**Seal:** `FINISHED_PARTIAL_LOOP` · Order Desk = PARKED mirror RO (nie LIVE)

---

## Pasy

| # | Pas | Stan |
|---|-----|------|
| A | VHQ Decision Instrument (S1–S6 + S8) | **DONE** |
| A2 | VHQ Final Dashboard | **DONE** |
| C0 | Order Desk SoT discovery | **DONE · ACCEPTED** |
| C1 | Order Desk thin WV (mirror RO) | **DONE · DEPLOY PASS** `vhq-w68a` |
| B | Growth / Demand (COM-AI) | **SHIP DEPLOYED** · widget disclosure LIVE · organic ≥2026-08-02 · counsel TAK · Ads freeze do 2026-08-06 |
| C | Order Desk / S7 LIVE | **PARKED** (`blocked_sot` · EV-W2-010) |
| D | 3D · MKT-ASSET · Ads freeze | **PARKED** |

## STOP

Fake S7 · Order LIVE · deploy bez GO · Ads w freeze · stage dirty `MKT/`
