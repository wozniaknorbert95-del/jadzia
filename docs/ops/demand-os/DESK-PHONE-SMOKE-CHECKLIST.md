---
status: "[ACTIVE · ETAP 4 OPS]"
title: "Biuro Popytu — phone / prod smoke"
updated: "2026-08-03"
gate: "DEMAND-OS-MARKETING-4-00"
master_todo: "docs/ops/demand-os/MASTER-TODO-4.md"
url: "https://api.zzpackage.flexgrafik.nl/commander/?view=demand-desk&cb=desk-dash09"
---

# Phone / prod smoke — Biuro Popytu (Etap 4 OPS)

## UX repair (desk-dash09)

- [ ] Cache `desk-dash09` (HTML/SW)
- [ ] F1: brak sticky `BRAK POŁĄCZENIA` przy status 200 (`#desk-connection-banner[hidden]` → display none)
- [ ] F2: chip `Cadence PARKED · publish LOCKED` w header (API `diagnostics.live_cadence`)
- [ ] F3: phone 375 — jedna kolumna; Diagnostyka / footer actions klikalne nad bottom-nav
- [ ] F4: Robota dnia czytelna w first viewport; ICP w `<details>`
- [ ] F5: GOTOWY label zawiera `(kalendarz · bez publish)`
- [ ] F6: Anuluj w confirm → brak API (toast tylko po Potwierdź)
- [ ] F7: footer human line (Zaufanie · Cadence · Następny); Doctor/Gate w Diagnostyka

## Footer honesty

- [ ] API status: `footer.doctor_scope` = `full`
- [ ] `footer.doctor_ok` matches VPS `hub doctor` (no false green)
- [ ] UI doctor chip shows OK/FAIL for full scope (not lightweight "files" as PASS)

## Desk

- [ ] `diagnostics.live_cadence` = PARKED (env GO ≠ unlock)
- [ ] No agent push to live publish

## Historical 5f

Agent prod verify §8: [`2026-08-03-DEMAND-DESK-5F-P2-01-SECTION8-CLOSE.md`](../../handoffs/2026-08-03-DEMAND-DESK-5F-P2-01-SECTION8-CLOSE.md)
