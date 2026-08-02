---
gate: DEMAND-OS-DASHBOARD-00
status: CLOSE · GAP-CLOSE SEAL
updated: 2026-08-02
---

# CLOSE — Demand Desk GAP-CLOSE (S1–S5)

## Delivered

- **B1** `refresh()` — tylko `loadDemandDesk` gdy active=demand-desk; per-loader try/catch
- **B2** top assets: `a.asset || a.asset_id`
- **B3** VHQ marketing-studio → Biuro Popytu + Desk Etap 5 KPI
- **U24** HTML: praca (B) przed puls (A)
- **dual_cash** kolumny + RED w UI
- **§8 link** design w footer
- **Cache** `desk-dash02`
- **Tests** 50 PASS (+ extended API icp/ledger)

## Hard DoD 15/15

All TRUE po gap-close + agent §8 rerun (JWT session stable on refresh).

## Evidence

```bash
python tools/demand_os_hub.py doctor
python -m pytest tests/unit/test_demand_desk_ui_contracts.py tests/test_demand_desk_api_extended.py tests/test_demand_os_api_desk.py -q
```

## Deploy

**VPS:** wymaga `GO DEPLOY COMMANDER UI` (Zasada 11).  
Lokalny commit gotowy — nie push bez GO jeśli polityka Dowódcy.

## Next human

1. GO deploy UI → VPS `/commander`
2. Dowódca §8 visual PASS w prod
3. `GO MARKETING HITL`
