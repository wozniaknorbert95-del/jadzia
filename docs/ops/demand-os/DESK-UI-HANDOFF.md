---
status: "[ACTIVE · ETAP 5 UI HANDOFF]"
updated: "2026-08-02"
design: "DEMAND-CONTROL-PANEL-DESIGN.md"
contract: "DESK-CONTRACT.md"
surface: "commander-ui #view-demand-desk"
---

# Biuro Popytu — UI handoff (implementacja)

## Powierzchnia

- **View:** `#view-demand-desk` — **default landing** (`/commander/` bez `?view=`)
- **Nav desktop:** Biuro Popytu · Kolejka (`#view-home`) · Analityka · Agenci · Ustawienia · Więcej
- **Nav mobile:** Biuro Popytu · Kolejka · Analityka · Agenci · Więcej
- **Więcej:** VHQ · Marketing legacy · Audyt · Ustawienia · OS · VCMS
- **API:** `GET /api/v1/commander/demand-os/status`
- **Deep link:** `?view=demand-desk` (opcjonalny; default bez parametru)
- **Cache:** `desk-dash05`

## Komponenty (reuse tokens)

| Komponent | Klasa bazowa | Opis |
|-----------|--------------|------|
| Header A0 | `.demand-desk-header` | ICP, tydzień, stan, robota dnia |
| KPI tile | `.kpi-grid` / `.kpi-tile` | Puls kasy A |
| Queue row | `.desk-queue-row` | HITL / Hunt B |
| Alert banner | `.demand-desk-banner` | FIXTURE, PARKED, dual-cash |
| Footer | `.demand-desk-footer` | data_mode, doctor, gate |
| Actions | `.buttonish` min 44px | max 4 akcje |

## Stany UI

| Stan | Trigger | UX |
|------|---------|-----|
| loading | fetch start | skeleton `.state-empty` |
| ok | 200 + render | pełny layout |
| BRAK_POŁĄCZENIA | network/500 | banner + retry |
| scope_denied | 403 | banner brak scope |
| PARKED | `state=PARKED` | badge + cash_warning |
| FIXTURE/MIXED | `data_mode` | `.demand-desk--fixture` root |
| parked_stop | `robota_dnia.code` | czerwony akcent A0 |
| stale | `footer.stale_warn` | hint stopka |
| empty_hitl/hunt/e | puste tablice | hint PL |

## Akcje (dry only)

1. HITL GOTOWY/BLOKADA → `POST …/hitl/decision`
2. ICP → `POST …/memory/icp`
3. Ledger Pon → `POST …/ledger/ensure-today`
4. Hunt dry → `POST …/hunt/dry`

**Zakaz:** one-click publish · reuse marketing publish handlers.

## RBAC

- `viewer`: read-only (disable act buttons)
- `delegat`/`dowodca`: act enabled
- 403 → toast backup

## Test IDs

Kontrakt: [`tests/unit/test_demand_desk_ui_contracts.py`](../../tests/unit/test_demand_desk_ui_contracts.py)

## Known gaps Etap 5b — agent CLOSED (2026-08-02)

Spec: [`2026-08-02-demand-desk-hardening-design.md`](../../superpowers/specs/2026-08-02-demand-desk-hardening-design.md)

- ~~Hard DoD 12/15~~ → **14/15 agent PASS** (pytest 75 · E2E flow static)
- ~~Prod data EMPTY~~ → sanitized pack + `demand_os_sync_set_now.sh` + `.env.example`
- ~~Layout AB/CD~~ → `#desk-ab-row` / `#desk-cd-row` @768+
- ~~E2E~~ → `tests/e2e/test_demand_desk_flow.py` + phone checklist

**Open (Dowódca only):** design §8 prod smoke · deploy GO · Hard DoD #12
