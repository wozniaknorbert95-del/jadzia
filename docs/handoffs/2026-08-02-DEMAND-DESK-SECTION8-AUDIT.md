---
gate: DEMAND-DESK-SECTION8
status: PASS · gap-close rerun
updated: 2026-08-02
cache: desk-dash02
---

# §8 Checklist — Demand Desk (post gap-close)

**Verdict: PASS** (agent browser + API, lokalnie :8765)

## Results

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | Deep link `?view=demand-desk` | PASS | URL lands on Biuro Popytu |
| 2 | Nav desktop + mobile More | PASS | `bindNavButtons` · Biuro Popytu current |
| 3 | A0→B→A→C→D→E→F sections | PASS | Praca dziś before Puls kasy in DOM |
| 4 | JWT session + Odśwież | PASS | B1: refresh scope-aware; session persists after Odśwież |
| 5 | Top wizard assets | PASS | B2: `tt_w32_install_01 — 2 startów` (not `?`) |
| 6 | VHQ Marketing Studio CTA | PASS | B3: `Otwórz Biuro Popytu` · `Desk Etap 5 LIVE` |
| 7 | Design §8 link in footer | PASS | `Design v2.1 · checklist §8` visible |
| 8 | HITL/hunt dry (no live publish) | PASS | Calendar rows + dry buttons; API tests PASS |

## Bugs closed

- **B1** refresh cleared JWT → fixed (`authCritical`, scope-aware `refresh()`)
- **B2** assets `?` → fixed (`a.asset || a.asset_id`)
- **B3** VHQ drift → fixed (marketing-studio action + KPI)

## Verify commands

```bash
python tools/demand_os_hub.py doctor
python -m pytest tests/unit/test_demand_desk_ui_contracts.py tests/test_demand_desk_api_extended.py tests/test_demand_os_api_desk.py -q
```

## Deploy

VPS Commander UI: **COMMAND_BLOCK** until `GO DEPLOY COMMANDER UI` (Zasada 11).
