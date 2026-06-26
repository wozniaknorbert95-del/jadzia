# DEPLOY-01 proof — INT-002 E2E

**Date:** 2026-06-26  
**Gate:** DEPLOY-01  
**Status:** **PARTIAL PASS** (smoke OK; Mollie E2E pending)

## Checklist

- [x] Smoke curl `SMOKE-1` → `db_status: success`
- [ ] Mollie test order → real WC `order_id` in `orders`
- [x] jadzia deployed (`a22c3d6` on VPS)
- [x] zzpackage theme deployed (GHA run 28231465724)
- [x] wp-config `FG_JADZIA_*` constants set (backup created on Cyber-Folks)

## Proof (bez PII)

| Field | Value |
|-------|-------|
| smoke_order_internal_id | 1 |
| e2e_wc_order_id | _pending Mollie test_ |
| deploy_jadzia_commit | a22c3d6 |
| deploy_theme_gha | 28231465724 |
| smoke_response | `{"db_status":"success","order_internal_id":"1"}` |

## Secrets location (nie w repo)

- jadzia VPS: `/root/jadzia/.env` (`WC_WEBHOOK_SECRET`, `LEADS_API_KEY`)
- zzpackage: `wp-config.php` (`FG_JADZIA_WEBHOOK_*`)

## Zamknięcie gate (po Mollie)

1. INT-002 → **LIVE** w `flexgrafik-meta/integration-contracts.md`
2. `todo.json`: DEPLOY-01 → `completed`, P1-02 → `pending`

---
RECOMMENDED_NEXT: Mollie test order w Wizard (test mode)
WHY_NEXT: Ostatni krok E2E WC → jadzia
