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

**PASS (prod)** — tip `96131f8` · cache `desk-dash09` · browser + static smoke OK.

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

### Deploy

- Commit: `96131f8` → `origin/master`
- VPS: `rev-demand-01-deploy-vps.sh 96131f8` → **PASS** · `systemctl active` · health OK
- URL: `https://api.zzpackage.flexgrafik.nl/commander/?view=demand-desk&cb=desk-dash09&_sw=1`

### Prod browser smoke (375 + desktop)

| Check | Result |
|-------|--------|
| F1 sticky disconnect | PASS — `hidden=true` · computed `display:none` |
| F2 cadence chip | PASS — `Cadence PARKED · publish LOCKED` |
| F3 phone + Diagnostyka | PASS — full-width · summary click · clear of bottom-nav |
| F4 robota / ICP | PASS — robota visible · ICP in details |
| F5 GOTOWY copy | PASS — `(kalendarz · bez publish)` |
| F6 Anuluj dry | PASS — `apiCalled=false` po Anuluj |
| F7 human footer | PASS — `Zaufanie: MIXED · Cadence: PARKED · Następny: …` |

Checklist: [`DESK-PHONE-SMOKE-CHECKLIST.md`](../ops/demand-os/DESK-PHONE-SMOKE-CHECKLIST.md)

## Świadomie odroczone

- Full axe / Lighthouse
- Legacy VHQ/Marketing poza a11y tree (H9)
- Visual rebrand poza monospace (H10)

## NEXT

1. Live P0 nadal PARKED — tylko po podpisie [`UNLOCK-LIVE-P0.md`](../ops/demand-os/UNLOCK-LIVE-P0.md)
2. (opcjonalnie) fala H9/H10 po trust seal
