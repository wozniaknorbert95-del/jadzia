---
todo: DOS-W1-01
os_target_section_ref: "Agent_Growth_Lead · H · C.1 #8 · K"
status: done
set_at: "2026-08-01"
---

# Money Check Ops — Growth Lead (Wave1)

**Nie dashboard.** Jedna prawda: [`LEDGER.csv`](./LEDGER.csv) + ten rytm.

## Rytm

| Kiedy | Co |
|-------|-----|
| **Każdy Pon** | 1 wiersz w [`MONEY-CHECK-LOG.csv`](./MONEY-CHECK-LOG.csv) |
| Źródła | sumuj `wizard_starts` / `paid` z LEDGER; `FAIL` z [`VALIDATOR-LOG.csv`](./VALIDATOR-LOG.csv) |
| Top hook | `asset_id` z najwyższym `wizard_starts` w tygodniu |
| Kill vanity | 1 zdanie: czego **NIE** robimy (HQ / dash / Ads / Wave2) |
| One improvement | **1** zmiana z episodic — nie nowy agent |

## Kalendarz F0 / W1 (Pierwsze Pony)

| Pon | Week | Status |
|-----|------|--------|
| 2026-08-03 | W32 | **NEXT live** (po organic ≥2026-08-02) |
| 2026-08-10 | W33 | slot |
| 2026-08-17 | W34 | slot (cel: pokrycie ledger 2 tyg. → W1 PASS) |

## Baseline 2026-08-01 (DOS-W1-01)

| Pole | Wartość |
|------|---------|
| starts UTM | 0 |
| paid | 0 |
| top hook | `tt_w31_install_01` (draft / Validator PASS) |
| FAIL count | 0 |
| compliance | 100% (0 FAIL / 0 bypass) |
| kill vanity | NO dashboard · NO HQ · NO Ads · NO Wave2 · NO ops desk |
| one improvement | każdy publish = wiersz w VALIDATOR-LOG najpierw |

## Procedura 5 min (Pon)

1. Otwórz LEDGER — zsumuj starts/paid od ostatniego Pon  
2. Otwórz VALIDATOR-LOG — policz `decision=FAIL`  
3. Wpisz wiersz w MONEY-CHECK-LOG  
4. Skopiuj 1-liner do LEDGER `notes` (Money Check YYYY-MM-DD)  
5. STOP — wróć do TT/STL, nie buduj ekranu

## Zakaz

Views · VHQ · tickets ops · „ładny wykres” bez UTM starts.
