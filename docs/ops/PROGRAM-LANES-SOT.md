---
status: "[APPENDIX]"
title: "Program lanes — DONE vs WAITING (ściąga, nie plan)"
updated: "2026-07-31"
owner: "Dowódca + agent"
tip: "local FINAL PRECLOSE · cache vhq-w67a · runtime prod still adafd83 until GO DEPLOY"
cache: "vhq-w67a"
parent_program: "docs/ops/FLEXGRAFIK-VIRTUAL-HQ-PROGRAM.md"
todo: "todo.json"
scorecard: "docs/ops/VHQ-DECISION-INSTRUMENT-SCORECARD.md"
---

# Program lanes — ściąga DONE / WAITING

**To nie jest plan of record.**  
Wygrywa: **Knowledge Index** → **`todo.json`** → **VHQ-PROGRAM** → DI scorecard.  
Ten plik = krótka mapa ADHD.

**Prod VHQ:** https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w66a  
**Active gate:** `VF-VHQ-FINAL-00` · cache target `vhq-w67a`

---

## Pasy

| # | Pas | Stan |
|---|-----|------|
| A | VHQ Decision Instrument (S1–S6 + S8) | **DONE** |
| A2 | VHQ Final Dashboard (nav + Finish Cards) | **ACTIVE** `VF-VHQ-FINAL-00` |
| B | Growth / Demand (COM-AI → organic → paid) | **PARKED** during FINAL |
| C | Order Desk / S7 | **PARKED** (`blocked_sot` · EV-W2-010) |
| D | 3D · MKT-ASSET · Ads freeze · Campus residual | **PARKED** |

```text
DONE (A DI + FIRM-IA) → ACTIVE (A2 FINAL) → later (B Growth / C Order)
```

---

## DONE

- DI S3–S6+S8 = 5
- VF-VHQ-FIRM-IA-00 — DEPLOY PASS runtime `adafd83` / `vhq-w66a`
- VHQ W1–W7 · Ops Bus · Vault L2

## PARKED / CZEKA

- COM-AI-50 — parked_during_final (pack ready)
- S7 / Order Desk — EV-W2-010
- Ads — freeze do 2026-08-06
- MKT-ASSET / 3D — osobne GO

## STOP

Fake S7 · Order LIVE · deploy bez GO · Ads w freeze · stage dirty `MKT/` · dual nav P0–P3+Firm Chain
