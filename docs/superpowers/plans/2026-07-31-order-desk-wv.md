# VF-ORDER-DESK-WV-00 Implementation Plan

> **For agentic workers:** Execute tasks in order. Thin read-only UI. No unpark.

**Goal:** Honest mirror Work View per ACCEPTED SoT D4.  
**Spec:** `docs/superpowers/specs/2026-07-31-order-desk-wv-design.md`  
**Cache:** `vhq-w68a`

### Task 1: API projection

- [x] Extend `db_list_orders` SELECT with `payment_status`, `paid_at`, `currency`
- [x] Existing `/api/v1/orders` returns new fields (no new route)

### Task 2: UI Work View

- [x] HTML section `#vhq-work-order-mirror`
- [x] JS fetch+render on order-desk open; ops always `insufficient_data`
- [x] Update `VHQ_ROOMS["order-desk"].sotLabel` to SoT ACCEPTED · mirror RO
- [x] Keep `status: PARKED` · `evidence: EV-W2-010`

### Task 3: Cache + tests + PRECLOSE

- [x] Bump `vhq-w67a` → `vhq-w68a` (html/sw hint)
- [x] `tests/unit/test_vhq_order_desk_wv_contracts.py`
- [x] pytest pass · PRECLOSE · no deploy without GO
