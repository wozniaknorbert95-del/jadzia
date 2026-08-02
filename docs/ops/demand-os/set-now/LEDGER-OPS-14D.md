---
todo: DOS-LEDGER-2W
os_target_section_ref: "O #3 · C.7"
status: in_progress
set_at: "2026-08-01"
window_start: "2026-08-01"
window_end: "2026-08-14"
sprint: "../ORGANIC-AGENCY-SPRINT-14D.md"
---

# Ledger Ops — 14 dni (DOS-LEDGER-2W)

**SoT plik:** [`LEDGER.csv`](./LEDGER.csv)  
**Sprint:** [`../ORGANIC-AGENCY-SPRINT-14D.md`](../ORGANIC-AGENCY-SPRINT-14D.md)  
**Reguła:** ≥1 wiersz / dzień · dziura max &lt;48h · **nie** fake `publish_Y=Y` bez real publish.

## Okno audit

| Dzień | date | status |
|-------|------|--------|
| 0 | 2026-08-01 | **DONE** (STL + sprint D0 SoT row) |
| 1 | 2026-08-02 | TT#1 + Hunt g2 — wpisz po aktywności |
| 2 | 2026-08-03 | Pon Money Check + Hunt |
| 3–13 | 2026-08-04 … 08-14 | daily (TT/FB/blog/trust) |
| PASS | po 14 dniach bez luk &gt;48h | `DOS-LEDGER-2W` → done |

## Daily 60s

1. Otwórz LEDGER.csv  
2. Dodaj wiersz `date=dziś` (nawet jeśli publish=N: comments/hot/starts)  
3. Jeśli publish TT: Validator-LOG PASS najpierw  
4. Pon: Money Check LOG  

## Zakaz

Dashboard zamiast wiersza · pomijanie dnia „bo zero” (wpisz zero).
