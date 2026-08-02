---
gate: DEMAND-OS-DASHBOARD-00
status: CLOSE · SEAL PARTIAL (audit 2026-08-02)
updated: 2026-08-02
---

# CLOSE — Etap 5 Dashboard Biuro Popytu (audit dogłębny)

## Werdykt

**Kod dashboardu istnieje i testy static/API przechodzą — ale pełny SEAL tool 100% był ogłoszony za wcześnie.**

## Hard DoD — audyt szczery

| # | Punkt | Status | Uwaga |
|---|-------|--------|-------|
| 1 | HTML A0–F + stopka | **PASS** | IDs zgodne z kontraktem testów |
| 2 | Render 1:1 status API | **PASS*** | *static code review; brak E2E |
| 3 | FIXTURE/PARKED/n/a val | **PASS** | banner + logika val w JS |
| 4 | HITL bez publish | **PASS** | osobny handler, brak „Opublikować” |
| 5 | Hunt dry + refresh | **PASS*** | API test OK; brak testu UI reload SENT |
| 6 | ICP + ledger | **PASS*** | brak dedykowanych testów API icp/ledger |
| 7 | VHQ CTA + n/a enrich | **PASS** | |
| 8 | Deep link ?view= | **PASS** | vhqBoot |
| 9 | brak go_ready hero | **PASS** | diagnostics w `<details>` |
| 10 | Static tests + nav 5 | **PASS** | po fix cache hint |
| 11 | doctor + pytest demand_os | **PASS** | 90 passed |
| 12 | Manual §8 Dowódca | **FAIL** | wcześniej fałszywie „agent PASS” |
| 13 | DESK-UI-HANDOFF.md | **PASS** | |
| 14 | CLOSE + evidence | **PASS** | ten plik |
| 15 | marketing PARKED_LAST | **PASS** | |

**Wynik: 12/15 PASS · 3 PARTIAL/FAIL → SEAL PARTIAL**

## Bugi znalezione w audycie (naprawione w tej sesji)

1. **Mobile More sheet** — `#more-to-demand-desk` bez handlera (martwy przycisk). Fix: `bindNavButtons(".more-sheet-btn[data-view]")`.
2. **RBAC viewer** — ICP submit i Ledger nie były disable. Fix: `deskApplyActButtons` na wszystkie `.desk-act-btn`.
3. **Test cache bust** — fail bo hint VHQ nadal miał tekst `vhq-w68a`. Fix: hint → `desk-dash01`.

## Luki pozostałe (nie blokują kodu, blokują pełny SEAL)

- **U4:** brak E2E/browser — tylko grep w plikach
- **U24:** hierarchia wizualna A0>B>A — w DOM kolejność A0→A(puls)→B(praca)
- **dual_cash:** UI pokazuje `open_fail`, nie kolumny verdict/offerte_only
- **Manual §8:** Dowódca musi otworzyć Commander i przejść checklist design
- **VPS deploy:** COMMAND_BLOCK (Zasada 11)

## Verify (2026-08-02)

```bash
python tools/demand_os_hub.py doctor
python -m pytest tests -k demand_os -q
python -m pytest tests/unit/test_demand_desk_ui_contracts.py tests/unit/test_commander_complete_ui.py -q
```

## Next human

1. Otwórz Commander → Biuro Popytu (desktop nav + mobile More sheet)
2. Checklist §8 w `DEMAND-CONTROL-PANEL-DESIGN.md`
3. Po PASS: `GO MARKETING HITL` + ewentualnie GO deploy UI
