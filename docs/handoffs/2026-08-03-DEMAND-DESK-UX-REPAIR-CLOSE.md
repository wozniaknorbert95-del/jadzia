---
status: CLOSE
title: Demand Desk UX Repair (post-audit FAIL)
date: 2026-08-03
cache: desk-dash09
source_audit: docs/handoffs/2026-08-03-DEMAND-DESK-UX-AUDIT-REPORT.md
surface: commander-ui/#view-demand-desk
live_publish: none
---

# Demand Desk UX Repair — CLOSE

## Verdict

**PASS (local / static)** — Critical/High z audytu UX naprawione w `commander-ui`.  
**Prod:** wymaga deploy + smoke `?cb=desk-dash09` (Zasada 11 — brak autonowego deploy w tej sesji).

## DoD

| # | Kryterium | Status |
|---|-----------|--------|
| F1 | Zero sticky BRAK POŁĄCZENIA przy status 200 | PASS — `#desk-connection-banner[hidden]{display:none!important}` |
| F2 | UI pokazuje cadence PARKED | PASS — chip `Cadence PARKED · publish LOCKED` z `diagnostics.live_cadence` |
| F3 | Phone 375: 1 kolumna, Diagnostyka klikalna | PASS — full-width + `padding-bottom` pod bottom-nav |
| F4 | Robota dnia hero; ICP secondary | PASS — większy type; ICP w `<details>` |
| F5 | GOTOWY = kalendarz · bez publish | PASS — suffix na CTA |
| F6 | Anuluj dry nie woła API | PASS — `if (!confirmed?.ok) return` (bug: object zawsze truthy) |
| F7 | Footer human line + doctor w Diagnostyka | PASS — `desk-human-line`; Doctor/Gate w details |
| — | Brak live publish path | PASS — bez zmian ścieżki publish |

## Pliki

- `commander-ui/styles.css` — banner hidden, phone layout, robota/chip/footer styles
- `commander-ui/index.html` — cadence chip, ICP details, human footer, cache `desk-dash09`
- `commander-ui/app.js` — cadence render, human line, HITL/hunt confirm fix, hunt disable fix
- `commander-ui/sw.js` — `coi-commander-desk-dash09`
- `tests/unit/test_demand_desk_ui_contracts.py` — cache + honesty guards
- `tests/unit/test_commander_complete_ui.py` — cache bump
- `docs/ops/demand-os/DESK-PHONE-SMOKE-CHECKLIST.md`
- `docs/ops/demand-os/DESK-UI-HANDOFF.md` — cache pointer

## Verify

```bash
pytest tests/unit/test_demand_desk_ui_contracts.py tests/unit/test_commander_complete_ui.py -q
# → 46 passed
```

Prod (po GO deploy):

```text
https://api.zzpackage.flexgrafik.nl/commander/?view=demand-desk&cb=desk-dash09
```

Checklist: [`DESK-PHONE-SMOKE-CHECKLIST.md`](../ops/demand-os/DESK-PHONE-SMOKE-CHECKLIST.md)

## Świadomie odroczone

- Full axe / Lighthouse
- Legacy VHQ/Marketing poza a11y tree (H9)
- Visual rebrand poza monospace (H10)

## NEXT

1. Dowódca: GO deploy tip + smoke phone 375 na `desk-dash09`
2. Live P0 nadal PARKED — tylko po podpisie [`UNLOCK-LIVE-P0.md`](../ops/demand-os/UNLOCK-LIVE-P0.md)
