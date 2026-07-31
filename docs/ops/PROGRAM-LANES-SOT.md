---
status: "[APPENDIX]"
title: "Program lanes — DONE vs WAITING (ściąga, nie plan)"
updated: "2026-07-31"
owner: "Dowódca + agent"
tip: "FINAL DEPLOY · cache vhq-w67a · seal FINISHED_PARTIAL_LOOP"
cache: "vhq-w67a"
parent_program: "docs/ops/FLEXGRAFIK-VIRTUAL-HQ-PROGRAM.md"
todo: "todo.json"
scorecard: "docs/ops/VHQ-DECISION-INSTRUMENT-SCORECARD.md"
---

# Program lanes — ściąga DONE / WAITING

**To nie jest plan of record.**  
Wygrywa: **Knowledge Index** → **`todo.json`** → **VHQ-PROGRAM** → DI scorecard.

**Prod VHQ:** https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w67a  
**Seal:** `FINISHED_PARTIAL_LOOP` (Director Dashboard — nie pełna fabryka)

---

## Pasy

| # | Pas | Stan |
|---|-----|------|
| A | VHQ Decision Instrument (S1–S6 + S8) | **DONE** |
| A2 | VHQ Final Dashboard (nav F7 + Finish Cards) | **DONE · VERIFY PASS** |
| C0 | Order Desk SoT discovery | **NEXT SESSION** `VF-ORDER-DESK-SOT-00` |
| B | Growth / Demand (COM-AI → organic → paid) | **HITL parallel** ACCEPT copy |
| C | Order Desk / S7 build | **PARKED** until SoT accept (`blocked_sot`) |
| D | 3D · MKT-ASSET · Ads freeze · Campus residual | **PARKED** |

## STOP

Fake S7 · Order LIVE · deploy bez GO · Ads w freeze · stage dirty `MKT/`
