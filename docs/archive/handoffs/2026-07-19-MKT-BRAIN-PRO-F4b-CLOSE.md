# Handoff — MKT-BRAIN-PRO-F4b paste_ready CLOSE

**Date:** 2026-07-19  
**Gate:** MKT-BRAIN-PRO  
**Status:** F4b paste_ready **v1 LIVE** tip **`0ae8244`** · `MB_MODE=propose`

## Deliverables

- `agent/marketing/paste_ready.py` — templates boost/hold/block/generic
- `agent/marketing/governance.py` — persist + idempotent Commander ticket
- `agent/marketing/telegram_proposals.py` — APPROVE → paste, **no token**
- `agent/db.py` — `db_merge_marketing_shadow_payload`
- `tests/unit/test_mb_paste_ready.py` — matrix PASS

## Evidence

```
pytest: 14 passed (paste_ready + f2 governance)
VPS tip=0ae8244 MB_MODE=propose
paste_version 1
commander_ticket_id 15
cached_second True
executed False
=== F4B_PASTE_SMOKE_OK ===
```

## Hard PARK

Ads API create · Mollie/Purchase · Meta #1 HOLD (no reorder)

## Next

- Human: APPROVE w TG → dostaje paste (opcjonalnie)
- Agent: observe cycles · Data Health amber later
