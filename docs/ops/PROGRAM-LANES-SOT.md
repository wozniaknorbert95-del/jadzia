---
status: "[APPENDIX]"
title: "Program lanes — DONE vs WAITING (ściąga, nie plan)"
updated: "2026-07-31"
owner: "Dowódca + agent"
tip: "WV-00 PRECLOSE · cache vhq-w68a · seal FINISHED_PARTIAL_LOOP (prod still w67a until GO)"
cache: "vhq-w68a (local) / vhq-w67a (prod until deploy)"
parent_program: "docs/ops/FLEXGRAFIK-VIRTUAL-HQ-PROGRAM.md"
todo: "todo.json"
scorecard: "docs/ops/VHQ-DECISION-INSTRUMENT-SCORECARD.md"
order_desk_sot: "docs/ops/ORDER-DESK-SOT-v0.md"
---

# Program lanes — ściąga DONE / WAITING

**To nie jest plan of record.**  
Wygrywa: **Knowledge Index** → **`todo.json`** → **VHQ-PROGRAM** → DI scorecard.

**Prod VHQ (until GO):** https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w67a  
**Local next cache:** `vhq-w68a`

---

## Pasy

| # | Pas | Stan |
|---|-----|------|
| A | VHQ Decision Instrument (S1–S6 + S8) | **DONE** |
| A2 | VHQ Final Dashboard (nav F7 + Finish Cards) | **DONE · VERIFY PASS** |
| C0 | Order Desk SoT discovery | **DONE · ACCEPTED** |
| C1 | Order Desk thin WV (mirror RO) | **PRECLOSE · GO DEPLOY** `VF-ORDER-DESK-WV-00` |
| B | Growth / Demand (COM-AI → organic → paid) | **HITL parallel** ACCEPT copy |
| C | Order Desk / S7 LIVE | **PARKED** (`blocked_sot` · EV-W2-010) |
| D | 3D · MKT-ASSET · Ads freeze · Campus residual | **PARKED** |

## STOP

Fake S7 · Order LIVE · deploy bez GO · Ads w freeze · stage dirty `MKT/`
