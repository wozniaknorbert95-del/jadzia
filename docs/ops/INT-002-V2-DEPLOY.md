# INT-002 v2 consumer — manual deployment runbook

**Gate:** REV-R0-02C  
**Deploy authority:** Dowódca/operator only  
**Database:** SQLite is authoritative; back up before migration

## Hard prerequisites

Do not deploy until all are true:

1. REV-R0-02A classification/reconciliation changes are committed and integrated.
2. REV-R0-02B zzpackage producer changes are committed and reviewed.
3. Jadzia consumer is deployed before the zzpackage producer.
4. A fresh, verified backup of production `data/jadzia.db` exists.
5. No secret or customer PII is copied into handoffs or chat.

The current `master` base does not contain the uncommitted REV-R0-02A artifacts.
Resolve that integration gap before production execution.

## Preflight

From the reviewed Jadzia commit:

```powershell
pytest -q tests/unit/test_int002_v2.py `
  tests/unit/test_order_store.py `
  tests/unit/test_order_node.py `
  tests/unit/test_wc_order_webhook.py

python -m py_compile `
  core/models.py `
  agent/db.py `
  agent/nodes/order_node.py
```

Expected:

- v1 payload remains accepted;
- v2 real/test/unknown evidence validates;
- legacy schema migration preserves rows;
- v1 retry cannot erase stored v2 evidence;
- checkout IDs are unique across orders.

## Manual backup

Operator chooses a maintenance window and creates a consistent SQLite backup:

```bash
sudo -u jadzia sqlite3 /opt/jadzia/data/jadzia.db \
  ".backup '/opt/jadzia/data/jadzia-pre-int002-v2-YYYYMMDD-HHMMSS.db'"
```

Verify the backup opens:

```bash
sudo -u jadzia sqlite3 /opt/jadzia/data/jadzia-pre-int002-v2-YYYYMMDD-HHMMSS.db \
  "PRAGMA integrity_check;"
```

Required result: `ok`.

## Manual consumer deployment

Use the canonical repository deployment workflow. After the operator deploys
Jadzia and restarts `jadzia.service`, verify:

```bash
systemctl is-active jadzia.service
curl -fsS http://127.0.0.1:8000/health
```

Trigger schema initialization through the running application, then inspect:

```bash
sudo -u jadzia sqlite3 /opt/jadzia/data/jadzia.db \
  "PRAGMA table_info(orders);"

sudo -u jadzia sqlite3 /opt/jadzia/data/jadzia.db \
  "PRAGMA index_list(orders);"
```

Required columns include:

```text
schema_version currency total_net tax_total
payment_status payment_method payment_provider payment_mode paid_at
classification classification_reason is_test test_reason
checkout_id checkout_started_at checkout_environment attribution_json
```

Required index: `idx_orders_checkout_id`.

## Compatibility gate

Before deploying zzpackage:

1. Send the existing signed INT-002 v1 smoke payload.
2. Confirm HTTP 200 and `db_status=success`.
3. Confirm its row has `schema_version=int-002.v1`.
4. Send a signed redacted v2 fixture in test classification.
5. Confirm every v2 field is queryable from `orders`.
6. Confirm no payload body/customer identity appears in logs.

## Manual producer deployment

Only after consumer compatibility passes:

1. Configure explicit `FG_REVENUE_ENVIRONMENT=production` in WordPress.
2. Operator manually deploys the reviewed zzpackage theme artifact.
3. Follow the controlled E2E checklist from zzpackage:
   `docs/checklists/REV-R0-02C-controlled-e2e.md`.

Do not replay historical GA4 purchases.

## Rollback

1. Disable `FG_JADZIA_WEBHOOK_URL` to stop producer delivery.
2. Roll back the zzpackage theme artifact.
3. Roll back Jadzia code.
4. Restore SQLite only if migration/data integrity failed and after explicit
   operator approval; additive columns alone do not require destructive restore.

## Completion

REV-R0-02 closes only after:

- controlled Mollie test order is stored as `test` and excluded from KPI;
- one authorized real paid attributable order matches WC, Jadzia, and GA4;
- reconciliation reports zero unresolved normalized duplicates in the proof window.
