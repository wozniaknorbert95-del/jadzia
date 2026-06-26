# DEPLOY-01 proof — INT-002 E2E (CLOSED)

**Date:** 2026-06-26  
**Gate:** DEPLOY-01  
**Status:** **PASS — gate closed**

## Checklist

- [x] Smoke curl `SMOKE-1` → `db_status: success`
- [x] Real WC `order_id` in `orders` table
- [x] jadzia deployed and healthy on VPS
- [x] zzpackage theme + wp-config `FG_JADZIA_*` constants
- [x] Webhook log: `[FG Jadzia] Webhook OK`

## Proof

| Field | Value |
|-------|-------|
| e2e_method | `wp_cli_synthetic` (Mollie test_mode=OFF on prod) |
| e2e_wc_order_id | **3149** |
| customer_email | deploy01-int002-20260626164158@flexgrafik.nl |
| webhook_log | `Webhook OK order_id=3149 status=processing` |
| smoke_order_internal_id | 1 (SMOKE-1) |

### jadzia DB

```text
# Verify: sqlite3 ... SELECT order_id,status FROM orders WHERE order_id='3149';
```

## Follow-up (non-blocking)

- Optional: full Mollie UI test with test mode enabled for video proof (M1-E checklist)
- Order 3149 total=0.00 (free product) — webhook payload valid; revenue path proven

## Secrets location (nie w repo)

- jadzia VPS: `/root/jadzia/.env` (`WC_WEBHOOK_SECRET`, `LEADS_API_KEY`)
- zzpackage: `wp-config.php` (`FG_JADZIA_WEBHOOK_*`)
