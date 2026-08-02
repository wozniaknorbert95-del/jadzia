---
gate: DEMAND-OS-DESK-5D-00
status: CLOSE · IA SEAL agent · Dowódca §8 pending
updated: 2026-08-02
parent: docs/handoffs/2026-08-02-DEMAND-DESK-5C-IA-CLOSE.md
---

# CLOSE — Etap 5d Biuro Popytu IA SEAL (agent)

## Werdykt

**Profesjonalna naprawa IA zakończona po audycie 5c.** Jedna powierzchnia operacyjna dnia; VHQ/Marketing demoted.

## Priorytety wykonane (D0→D4)

| Faza | Deliverable | Status |
|------|-------------|--------|
| D0 | CSS `.more-sheet-btn` fix · copy sweep · desk-dash05 | ✅ |
| D1 | Kolejka=`#view-home` · VHQ tylko Więcej · `#vhq-enter`→Desk | ✅ |
| D2 | SoT sweep campus/scorecard/PROGRAM/DESK-UI-HANDOFF | ✅ |
| D3 | 50 pytest IA gate (static E2E contracts) | ✅ |
| D4 | deploy + handoff | ✅ |

## Zmiany kluczowe

- **Landing:** `/commander/` → Biuro Popytu (bez `?view=`)
- **Nav:** Biuro Popytu · **Kolejka** (nie VHQ Start) · Więcej → VHQ + Marketing legacy
- **Copy:** usunięto „Primary = Virtual HQ” z `#view-home`
- **Bug fix:** CSS more-sheet touch targets (regresja 5c)
- **Cache:** desk-dash05 · SW purge starych `coi-commander-*`

## IA tier (docelowe)

| Tier | Surface | Wejście |
|------|---------|---------|
| P0 | `#view-demand-desk` | default · nav first |
| P1 | `#view-home` (Kolejka) | nav · tickets/queue |
| P2 | `#view-marketing` | Więcej → legacy |
| P2 | `#view-hq` (VHQ) | Więcej → Mission Control |

## Verify

```bash
python -m pytest tests/unit/test_demand_desk_ui_contracts.py tests/e2e/test_demand_desk_flow.py tests/unit/test_commander_complete_ui.py tests/unit/test_vhq_firm_ia_contracts.py -q
```

**Wynik:** 50 passed.

Prod URL: `https://api.zzpackage.flexgrafik.nl/commander/?cb=desk-dash05`

## Dowódca — §8 (human, nie agent)

Checklist: [`DESK-PHONE-SMOKE-CHECKLIST.md`](../ops/demand-os/DESK-PHONE-SMOKE-CHECKLIST.md)

- [ ] Cold open → Biuro Popytu (nie VHQ theater)
- [ ] Kolejka → queue, nie Director Brief
- [ ] Więcej → VHQ opcjonalnie · Marketing legacy
- [ ] 7× checkbox §8 w [`DEMAND-CONTROL-PANEL-DESIGN.md`](../ops/demand-os/DEMAND-CONTROL-PANEL-DESIGN.md)

Hard DoD #12 → **15/15 dopiero po §8 prod**.

Marketing **PARKED_LAST**.
