# PLAN-DEPLOY-INT-002 — Revenue Ops E2E proof

**Status:** ACTIVE (gate)  
**Created:** 2026-06-26  
**Parent:** `docs/plans/PLAN-COI-PHASE-A.md`  
**Blocks:** P1-01, P1-02 (agent implementation)

---

## Goal

Prove INT-002 works end-to-end: WooCommerce (zzpackage) → jadzia `orders` table.

Code is **done** (P0-01/02/03). This plan is **deploy + verification only**.

---

## Gate criteria (DEPLOY-01 = completed when ALL true)

- [ ] `WC_WEBHOOK_SECRET` set on jadzia VPS `.env` and zzpackage `wp-config.php` (same value)
- [ ] jadzia-core deployed with `orders` schema + `POST /webhooks/woocommerce/order`
- [ ] zzpackage theme deployed with `inc/integrations/fg-jadzia-order-webhook.php`
- [ ] Smoke curl returns `db_status: success` (order_id `SMOKE-1`)
- [ ] Mollie test order → real WC `order_id` row in `orders`
- [ ] Handoff proof: `docs/handoffs/2026-06-26-deploy-int-002-proof.md`

---

## Faza 1 — Secrets (~15 min, Dowódca)

```bash
openssl rand -hex 32
```

| Side | Config |
|------|--------|
| jadzia VPS | `.env` → `WC_WEBHOOK_SECRET=<secret>` |
| zzpackage | `wp-config.php` → `define('FG_JADZIA_WEBHOOK_SECRET', '<secret>');` |

```php
define('FG_JADZIA_WEBHOOK_URL', 'https://185.243.54.115:8000/webhooks/woocommerce/order');
```

Ref: `zzpackage.flexgrafik.nl/docs/checklists/P0-03-jadzia-order-webhook.md`

---

## Faza 2 — Deploy jadzia-core (~20 min, Dowódca)

```bash
cd jadzia-core
./deployment/deploy-to-vps.sh
```

Script auto-backups `data/jadzia.db` before upload.

On VPS after deploy:

```bash
systemctl restart jadzia
curl -f http://localhost:8000/worker/health
```

---

## Faza 3 — Smoke receiver (~5 min, Dowódca)

```bash
SECRET="<secret>"
BODY='{"order_id":"SMOKE-1","status":"processing","items":[{"sku":"TEST","qty":1,"price":199}],"customer":{"email":"smoke@test.nl","name":"Smoke"},"total_gross":199,"payment_id":"tr_smoke"}'
SIG=$(printf '%s' "$BODY" | openssl dgst -sha256 -hmac "$SECRET" | awk '{print $2}')
curl -sS -X POST "http://185.243.54.115:8000/webhooks/woocommerce/order" \
  -H "Content-Type: application/json" \
  -H "X-WC-Signature: $SIG" \
  -d "$BODY"
```

Verify on VPS:

```bash
sqlite3 /root/jadzia/data/jadzia.db \
  "SELECT order_id,status,total_gross FROM orders WHERE order_id='SMOKE-1';"
```

---

## Faza 4 — Deploy zzpackage theme (~15 min, Dowódca)

Upload theme files:
- `flexgrafik-wizard-theme/inc/integrations/fg-jadzia-order-webhook.php`
- `flexgrafik-wizard-theme/functions.php` (require line 14)

Cyber-Folks deploy per zzpackage workflow.

---

## Faza 5 — Mollie E2E (~15 min, Dowódca)

1. Mollie test mode — complete Wizard checkout
2. WC order status → `processing` or `completed`
3. Logs: `[FG Jadzia] Webhook OK` (zzpackage), `[OrderNode] Order saved` (jadzia)
4. DB:

```bash
sqlite3 /root/jadzia/data/jadzia.db \
  "SELECT order_id,status,total_gross,payment_id FROM orders ORDER BY id DESC LIMIT 1;"
```

Must be **real WC order_id** (not SMOKE-1).

---

## Faza 6 — Close gate (Dowódca + agent)

1. Fill `docs/handoffs/2026-06-26-deploy-int-002-proof.md`
2. `flexgrafik-meta/docs/core/integration-contracts.md` → INT-002 status **LIVE**
3. `todo.json`: DEPLOY-01 → `completed`, P1-01 → `pending`

---

## Rollback

1. Comment `FG_JADZIA_WEBHOOK_URL` in wp-config (instant stop)
2. Restore jadzia DB from `jadzia.db.bak.*`
3. Remove theme `require_once` if needed

---

## After gate

| Order | Task | Owner |
|-------|------|-------|
| 1 | P1-01 `lead_node` + `POST /api/v1/leads` | agent |
| 2 | DEPLOY-02 lead E2E | Dowódca |
| 3 | P1-02 analytics snapshot | agent |
