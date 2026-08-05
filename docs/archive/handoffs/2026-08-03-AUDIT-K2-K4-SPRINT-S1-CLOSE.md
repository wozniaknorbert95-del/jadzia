---
status: CLOSE
title: "Audit Sprint S1 — K2 GA4 adapter + K4 plain-language labels"
date: 2026-08-03
tip: uncommitted (needs commit + cache bump)
cache: desk-dash09
branch: master
active_item: 4-AWAIT-UNLOCK
live_publish: none
---

# Session CLOSE — 2026-08-03 (Sprint S1)

## What

Audit K-roadmap Sprint S1: wdrożenie K2 (GA4 adapter w desk) + K4 (plain-language labels).

### K2: GA4 adapter → desk

- `commander_status.py`: GA4 `fetch_wizard_starts()` wołany w `build_demand_os_status()`
- Nowy blok `ga4` w payloadzie: `ok`, `mode`, `sessions`, `error`
- Nowy KPI: `ga4_sessions` w `kpi` + tile `Sesje GA4` w UI
- Fail-closed: stub mode domyślnie; live gdy `DEMAND_OS_GA4_LIVE=1` + creds
- GA4 sessions ≠ wizard starts — uczciwa etykieta, secondary signal

### K4: Plain-language labels

Zamienione etykiety w `index.html` + `app.js` + `desk_contract.py`:

| Było | Jest |
|------|------|
| HITL — kalendarz (bez publikacji) | Treści do zatwierdzenia |
| Hunt — dry komentarze | Komentarze testowe |
| Cadence PARKED · publish LOCKED | Publikowanie wstrzymane |
| GOTOWY (kalendarz · bez publish) | Zaplanuj (bez publikacji) |
| BLOKADA | Wstrzymaj |
| Starts UTM | Starty Wizard |
| WoW Δ | vs. tydzień |
| Paid | Płatne |
| Top hook | Najlepszy hook |
| Publish | Publikacje |
| Validator fail | Błędy walidacji |
| Gorące | Gorące leady |
| Top assety Wizard | Najlepsze treści (starty Wizard) |
| STL: open=X · breach=Y · overnight=Z | X otwartych · Y czeka >48h · Z bez odpowiedzi |
| Dual-cash open_fail: X · [cols] | X niespójności kasy |
| Money Check | Sprawdź kasę |
| Doctor / Gate / Kontrakt | System / Bramka / Wersja |
| data_mode: FIXTURE | Dane testowe |
| ostatni REAL | ostatnie dane |
| Robota dnia: CODE | Zadanie dnia: czytelna etykieta |
| SENT / BLOCK / READY | Wysłany / Wstrzymany / Gotowy |
| Dry komentarz (mock) | Wyślij komentarz testowy |

### Backend `desk_contract.py`

Dodano `_ROBOTA_LABELS` mapping: MONEY_CHECK→Sprawdź kasę, PUBLISH→Publikuj, HUNT→Kontaktuj klientów itd.
Zwraca `label` w robota payload.
`cash_warning` zmieniony na plain PL.

### Testy

- 2 testy zaktualizowane (`test_demand_desk_ui_contracts.py`, `test_render_desk_golden.py`) — nowe assertions matching plain-language
- 55/55 desk tests PASS
- 113 demand OS tests PASS (owner-verify)
- Pre-existing failures: `test_generate_resolves_empty_sku` (429 rate limit), `test_publish_entry_wrong_platform` (platform gate), `test_*_cache_vhq_w68a` (cache version) — **all unrelated**

### Audit plan

Brakujący plik `.cursor/plans/audit-k-roadmap.md` utworzony z DoD per K1–K14.

## Files changed

| File | Change |
|------|--------|
| `agent/demand_os/commander_status.py` | GA4 adapter import + call + payload blocks |
| `agent/demand_os/desk_contract.py` | `_ROBOTA_LABELS` + `label` field + PL cash_warning |
| `commander-ui/index.html` | All K4 label replacements + GA4 tile |
| `commander-ui/app.js` | All K4 dynamic label replacements + GA4 render |
| `tests/unit/test_demand_desk_ui_contracts.py` | Updated assertions |
| `tests/unit/test_render_desk_golden.py` | Updated assertions |
| `.cursor/plans/audit-k-roadmap.md` | NEW — K1–K14 roadmap with DoD |

## State

- `active_item`: `4-AWAIT-UNLOCK`
- `live_cadence`: PARKED
- VPS tip: `5fed869` (docs) / `96131f8` (runtime)
- Live P0: BLOCKED
- Ads: PARK cash

## Deploy note

Changes are **local only** — not committed, not deployed. Needs:
1. Commit
2. Cache bump (`desk-dash09` → `desk-dash10`)
3. VPS deploy with GO (Zasada 11)

## NEXT SESSION

1. **Cache bump** `desk-dash09` → `desk-dash10` (HTML + SW + tests)
2. **Commit + VPS deploy** (po GO)
3. **Sprint S2**: K1 REV_R1 attribution (first real wizard_start event) + K3 auth simplify
4. Live P0 nadal **PARKED**

```
DONE: [K2 GA4 adapter · K4 plain-language labels · audit K-roadmap · tests GREEN]
LEFT: [commit · cache bump · deploy · K1 attribution · K3 auth · K5–K14 tech debt]
RISKS: [GA4 still stub on VPS · auth still manual JWT · deploy needed for labels to go live]
NEXT_COMMAND_FOR_NEW_AGENT: commit + cache bump desk-dash10 → deploy GO request

---
CURRENT_STAGE: L3.5-PostCoding
RECOMMENDED_NEXT: Commit S1 changes + cache bump desk-dash10
WHY_NEXT: Labels i GA4 tile gotowe lokalnie — potrzebują commit + deploy żeby trafić do foundera
---
```
