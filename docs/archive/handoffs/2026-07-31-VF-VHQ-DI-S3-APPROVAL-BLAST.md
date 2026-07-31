---
status: "[BLAST]"
title: "VF-VHQ-DI-S3-APPROVAL — L2 parent↔companion sync"
updated: "2026-07-31"
gate: "VF-VHQ-DI-S3-APPROVAL"
cache_target: "vhq-w64a (API-only unless UI toast)"
---

# BLAST — VF-VHQ-DI-S3-APPROVAL

## Intent

Close S3.1: L2 Approve on companion **or** parent must sync peer state — no silent parent `pending` lie on bus trail.

S3.2–S3.3 already PASS (regression). S3.4: extend ops_bus tests for sync.

## Scope

- `agent/ops_bus/emit.py` — peer sync in `set_approval_state`
- `api/routes/ops_bus.py` — return `synced_event_ids`
- `tests/unit/test_ops_bus.py` — both directions
- scorecard/todo after dogfood

## STOP

No L3 execute · no Ads/Mollie · no Order LIVE · no MKT · side_effects remain false
