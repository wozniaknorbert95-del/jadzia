# Task 3 Report - VF-VHQ-FIRM-IA-00 Firm IA rooms

**Gate:** VF-VHQ-FIRM-IA-00  
**Task:** 3 - WP-B `firmStage` + unlock copy on rooms  
**Date:** 2026-07-31  
**Status:** DONE (GREEN)

## Deliverable

Updated `commander-ui/app.js` to add canonical `firmStage` and `firmRole` coverage across the VHQ room manifest, plus `unlockHint` on PARKED/PLANNED rooms that need explicit unlock honesty. Room detail rendering now shows `firmRole` and `unlockHint` through the existing `vhqFillRoomExtra(...)` path.

## Scope completed

- Added `firmStage` to all VHQ rooms covered by the WP-B brief, including `reception` as future `demand` and `design-agent-probe` as `direct`
- Added one-line `firmRole` copy for every mapped room
- Added `unlockHint` copy for deliver rooms that remain `PARKED`/`PLANNED`, including `order-desk`, `production-control`, `preflight-quality`, `dispatch-returns`, `supplier-dock`, `asset-warehouse`, and `partner-production-network`
- Preserved `order-desk` as `status: "PARKED"` with `evidence: "EV-W2-010"` and no fake LIVE KPI/unpark
- Rendered `firmRole` / `unlockHint` in room detail view with:
  - `vhqEl("p", "vhq-firm-role", room.firmRole)`
  - `vhqEl("p", "hint vhq-unlock-hint", room.unlockHint)`
- Expanded `tests/unit/test_vhq_firm_ia_contracts.py` to cover the full manifest mapping and render hooks

## TDD evidence

### RED

Command:

```bash
pytest tests/unit/test_vhq_firm_ia_contracts.py -v
```

Result before production changes: **3 failed, 3 passed**

- `test_firm_stage_on_room_manifest` failed because `firmStage` was missing from the manifest
- `test_room_panel_renders_firm_role_and_unlock_hint_copy` failed because room detail rendering did not append the new copy
- `test_deliver_rooms_keep_unlock_hints_without_fake_live_claims` failed because deliver rooms did not expose `unlockHint`

### GREEN

Command:

```bash
pytest tests/unit/test_vhq_firm_ia_contracts.py -v
```

Result after changes: **6 passed, 0 failed**

## Verification

- `ReadLints` on `commander-ui/app.js` and `tests/unit/test_vhq_firm_ia_contracts.py`: no linter errors
- No marketing staging touched; `docs/ops/marketing/MKT/**` remains out of scope
- No cache bump implemented in this task

## Commit

Planned message:

```text
feat(vhq): firmStage + PARKED role/unlock copy on VHQ rooms
```

## Concerns

- Manual browser smoke was not run in this task execution
- `Firm Chain` strip and cache bump remain intentionally out of scope for Task 4 / Task 5
