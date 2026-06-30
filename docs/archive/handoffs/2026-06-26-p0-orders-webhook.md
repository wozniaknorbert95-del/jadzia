# Handoff — P0-02 orders schema + P0-01 WC webhook (INT-002)

**Date:** 2026-06-26  
**Stage:** L4-Closed  
**Plan:** `docs/plans/PLAN-COI-PHASE-A.md`

## Done

| Task | Deliverable |
|------|-------------|
| **P0-02** | `orders` table in `jadzia.db` via `_init_schema()` + `db_upsert_order` / getters |
| **P0-01** | `agent/nodes/order_node.py` + `POST /webhooks/woocommerce/order` |

## Schema (`orders`)

- `order_id` (WC, UNIQUE), `status`, `items_json`, `customer_email`, `customer_name`
- `total_gross`, `payment_id`, `created_at`, `updated_at`
- Upsert on duplicate `order_id` (idempotent webhook retries)

## INT-002 contract

- **Request:** Pydantic `WooOrderWebhookRequest` — matches `integration-contracts.md`
- **Response:** `{ "db_status": "success|fail", "order_internal_id": "string" }`
- **Auth:** optional `WC_WEBHOOK_SECRET` + `X-WC-Signature` (HMAC-SHA256 hex); skipped when unset (dev)

## Files touched

- `agent/db.py` — schema + CRUD
- `agent/nodes/order_node.py` — new
- `api/routes/webhooks.py` — new (inbound; distinct from `api/webhooks.py` outbound)
- `api/app.py` — router registration
- `core/models.py` — Woo order models
- `tests/unit/test_order_store.py`, `test_order_node.py`, `test_wc_order_webhook.py`
- `tests/test_api_integration.py` — route list

## Verification

```bash
pytest tests/ -q
# 10 new tests + full suite green
```

Smoke (local):

```bash
curl -X POST http://localhost:8000/webhooks/woocommerce/order \
  -H "Content-Type: application/json" \
  -d '{"order_id":"TEST-1","status":"processing","items":[{"sku":"X","qty":1,"price":199}],"customer":{"email":"a@b.nl","name":"Test"},"total_gross":199,"payment_id":"tr_x"}'
```

## Next

- **P0-03** — WC webhook config on zzpackage (Dowódca checklist; blocked on agent)
- Set `WC_WEBHOOK_SECRET` on VPS + zzpackage before production traffic
- VPS: backup `data/jadzia.db` before first deploy with new schema

---
CURRENT_STAGE: L4-Closed
RECOMMENDED_NEXT: P0-03 (Dowódca — WC webhook on zzpackage)
WHY_NEXT: Backend ingestion ready; revenue path needs WooCommerce to POST to jadzia
