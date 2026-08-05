# HANDOFF — DEMAND-DESK-5F-P0 BLAST

**Date:** 2026-08-02  
**Gate:** `DEMAND-OS-DESK-5F-00`  
**Cache:** `desk-dash07`  
**Scope:** P0-01…P0-06 + P1 auth guards + P1-04 STL breach hint

## Done

| ID | Change |
|----|--------|
| 5F-P0-01 | VHQ manifest lazy (`vhqEnsureManifest`) · `#view-hq` inert/aria-hidden · no boot render |
| 5F-P0-02 | `openQueueView()` · CEO stubs filtered from `renderQueue` |
| 5F-P0-03 | `clearVhqUrlParam()` on Desk + Queue |
| 5F-P0-04 | MIXED/FIXTURE banner in desk header (prominent) |
| 5F-P0-05 | Hunt SENT optimistic UI + uppercase desk_status |
| 5F-P0-06 | Hide connection banner at load start when JWT present |
| 5F-P1-01..03 | Auth-required empty states (no infinite „Ładowanie…”) |
| 5F-P1-04 | STL breach warn copy |

## Verify

```text
pytest tests/unit/test_demand_desk_ui_contracts.py \
  tests/unit/test_commander_complete_ui.py \
  tests/e2e/test_demand_desk_flow.py \
  tests/test_hunt_dry_updates_queue.py
→ 48/48 PASS (local)
```

## Next

- **CURRENT pointer:** `5F-P1-01` (browser proof Analityka/Agenci/Marketing on prod)
- **Human:** `5F-P2-01` Dowódca §8 phone smoke
- **Deploy:** GO required (Zasada 11)

## Prod check (post-deploy)

`https://api.zzpackage.flexgrafik.nl/commander/?cb=desk-dash07`

- Desk cold open: no `?vhq=` · no Ponów ghost · MIXED banner visible
- Kolejka: queue only, no CEO stubs
- Więcej→VHQ: manifest mounts on first open
