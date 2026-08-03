---
status: "[SEALED · ETAP 5f UI · historical handoff]"
updated: "2026-08-03"
design: "DEMAND-CONTROL-PANEL-DESIGN.md"
contract: "DESK-CONTRACT.md"
surface: "commander-ui #view-demand-desk"
---

# Biuro Popytu — UI handoff (historical)

> **ACTIVE program pointer:** [`MASTER-TODO-4.md`](./MASTER-TODO-4.md) → OPS HARDENING SEALED.  
> Live P0 PARKED until [`UNLOCK-LIVE-P0.md`](./UNLOCK-LIVE-P0.md).

## Powierzchnia

- **View:** `#view-demand-desk` — **default landing** (`/commander/` bez `?view=`)
- **Nav desktop:** Biuro Popytu · Kolejka (`#view-home`) · Analityka · Agenci · Ustawienia · Więcej
- **Nav mobile:** Biuro Popytu · Kolejka · Analityka · Agenci · Więcej
- **Więcej:** VHQ · Marketing legacy · Audyt · Ustawienia · OS · VCMS
- **API:** `GET /api/v1/commander/demand-os/status` (full doctor in footer)
- **Deep link:** `?view=demand-desk` (opcjonalny; default bez parametru)
- **Cache:** `desk-dash09` (UX repair post-audit)
- **Master TODO (active):** [`MASTER-TODO-4.md`](./MASTER-TODO-4.md) · `4-TOOL-01`
- **UI SEAL archive:** [`MASTER-TODO-5F.md`](./MASTER-TODO-5F.md) · SEALED (not active)

## Footer honesty

- `footer.doctor_scope`: `full` (API) | `lightweight` (local builder default)
- `footer.doctor_ok`: **true only when scope=full and full doctor PASS**
- `footer.doctor_files_ok`: files-only slice (never shown as OK in UI)

## Komponenty (reuse tokens)

| Komponent | Klasa bazowa | Opis |
|-----------|--------------|------|
| Header A0 | `.demand-desk-header` | ICP, tydzień, stan, robota dnia |
| KPI tile | `.kpi-grid` / `.kpi-tile` | Puls kasy A |
| Queue row | `.desk-queue-row` | HITL / Hunt B |
| Alert banner | `.demand-desk-banner` | FIXTURE, PARKED, dual-cash |
| Footer | `.demand-desk-footer` | data_mode, doctor, gate |
| Actions | `.buttonish` min 44px | max 4 akcje |

## Akcje (dry only)

1. HITL GOTOWY/BLOKADA → `POST …/hitl/decision`
2. ICP → `POST …/memory/icp`
3. Ledger Pon → `POST …/ledger/ensure-today`
4. Hunt dry → `POST …/hunt/dry`

**Zakaz:** one-click publish · live TT/FB/blog · Ads.

## Closed

§8 prod smoke · Hard DoD 15/15 — [`2026-08-03-DEMAND-DESK-5F-CLOSE.md`](../handoffs/2026-08-03-DEMAND-DESK-5F-CLOSE.md)
