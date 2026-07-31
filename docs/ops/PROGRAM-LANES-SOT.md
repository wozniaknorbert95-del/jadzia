---
status: "[APPENDIX]"
title: "Program lanes — DONE vs WAITING (ściąga, nie plan)"
updated: "2026-07-31"
owner: "Dowódca + agent"
tip: "a05e762"
cache: "vhq-w66a"
parent_program: "docs/ops/FLEXGRAFIK-VIRTUAL-HQ-PROGRAM.md"
todo: "todo.json"
scorecard: "docs/ops/VHQ-DECISION-INSTRUMENT-SCORECARD.md"
---

# Program lanes — ściąga DONE / WAITING

**To nie jest plan of record.**  
Wygrywa: **Knowledge Index** → **`todo.json`** → **VHQ-PROGRAM** → DI scorecard.  
Ten plik = krótka mapa ADHD.

**Prod VHQ:** https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w66a  
**Tip of record:** `a05e762` (docs) · runtime `2623ae2` · cache `vhq-w66a`

---

## Pasy

| # | Pas | Stan |
|---|-----|------|
| A | VHQ Decision Instrument (S1–S6 + S8) | **DONE** |
| B | Growth / Demand (COM-AI → organic → paid po freeze) | **NEXT (human GO)** |
| C | Order Desk / S7 | **PARKED** (`blocked_sot` · EV-W2-010) |
| D | 3D · MKT-ASSET · Ads freeze · Campus residual | **PARKED** |

```text
DONE (A) → NEXT (B Growth, po GO) → later (C Order/S7 gdy desk istnieje)
```

---

## DONE

- DI S3–S6+S8 = 5 · tip `a05e762` / `vhq-w66a`
- VHQ W1–W7 · Ops Bus · Vault L2 · INC-SSH ok
- MVP honesty: Sales→Wizard→follow-up (`partial_loop`)

## PARKED / CZEKA

- VF-VHQ-FIRM-IA-00 — local CLOSE PASS · prod Founder dogfood czeka na `GO DEPLOY`
- S7 / Order Desk — brak biurka SoT (nie brak płatności)
- COM-AI-50 — `unblocked`, human przed organic ≥2026-08-02
- Ads — freeze do 2026-08-06
- MKT-ASSET / 3D — osobne GO

## STOP

Fake S7 · Order LIVE bez SoT · deploy bez GO · Ads w freeze · stage dirty `MKT/`

## Czytaj

| Potrzeba | Plik |
|----------|------|
| Ster sesji | `todo.json` |
| Produkt HQ | `docs/ops/FLEXGRAFIK-VIRTUAL-HQ-PROGRAM.md` |
| DI DoD | `docs/ops/VHQ-DECISION-INSTRUMENT-SCORECARD.md` |
| Hierarchia SoT | `docs/ops/KNOWLEDGE-SYSTEM-INDEX.md` |
| Marketing day | `docs/ops/marketing/OPERATOR-TODAY.md` |
