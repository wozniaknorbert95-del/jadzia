# Revenue reconciliation runbook — REV-R0-02

**Contract:** `docs/contracts/REVENUE-EVENT-CONTRACT-v1.md`  
**Scope:** legacy classification and read-only WooCommerce/GA4/Jadzia reconciliation  
**Safety:** history is classified, never deleted

## What this slice provides

- Append-only classifications: `real|test|unknown`.
- Deterministic rules for known E2E leads/orders/payment IDs.
- PII-free JSON reconciliation report.
- Canonical normalization of legacy GA4 `WC-{id}` to WooCommerce `{id}`.
- Commander visibility through `classification` and nullable `is_test`.
- Test-classified leads are excluded from the Commander hot-lead queue.
- Legacy destructive E2E cleanup is blocked.

This slice does not infer missing attribution or qualification. Missing evidence remains `unknown`.

## Dry-run report

Dry-run opens SQLite in read-only mode and performs no migration or write:

```powershell
$env:PYTHONPATH = "."
python scripts/revenue_reconcile.py --db data/jadzia.db --output revenue-report.json
```

Without a transaction-level GA4 export, the report correctly returns:

```json
{
  "ga4_order_reconciliation": {
    "status": "insufficient_evidence",
    "reason": "transaction_level_ga4_export_not_supplied"
  }
}
```

## Reconcile a GA4 transaction export

Accepted input:

```json
{
  "transaction_ids": ["WC-4201", "4202"]
}
```

Run:

```powershell
python scripts/revenue_reconcile.py `
  --db data/jadzia.db `
  --ga4-transactions ga4-transactions.json `
  --output revenue-report.json
```

The report normalizes `WC-4201` to `4201` for comparison but never edits source data.

## Apply classifications

This is an explicit database write. Before production use:

1. Stop and obtain Dowódca deploy/data approval.
2. Back up `data/jadzia.db`.
3. Run dry-run and review every `classification_candidate`.
4. Apply only after review:

```powershell
python scripts/revenue_reconcile.py `
  --db data/jadzia.db `
  --apply-classifications `
  --output revenue-report-applied.json
```

Apply behavior:

- appends to `revenue_classification_events`;
- never deletes or updates source rows;
- skips every entity that already has a classification;
- rerunning is idempotent;
- a human classification remains authoritative.

## Classification rules

Known test evidence includes:

- lead/session prefixes `deploy01-`, `deploy02-`, `int002-e2e-`, `int004-e2e-`, `e2e-`, `smoke-`;
- order prefixes `SMOKE-`, `DEPLOY-`, `E2E-`, `TEST-`;
- payment prefixes `tr_deploy`, `tr_test`, `tr_mollie_test`.

A production order is `real` only when:

- canonical numeric WooCommerce `order_id`;
- status `processing|completed`;
- payment ID present;
- total gross is at least €199;
- no deterministic test evidence exists.

Everything else remains `unknown` until evidence or human classification exists.

## Interpretation

| Field | Meaning |
|---|---|
| `classification` | Current persisted classification, or deterministic proposal when absent. |
| `persisted` | Whether an append-only decision already exists. |
| `kpi_paid_eligible` | `true` only for an order classified `real`. |
| `normalized_order_duplicates` | Multiple stored IDs resolve to one canonical WC order ID. |
| `missing_ga4_order_ids` | Jadzia non-test order without supplied GA4 transaction. |
| `ga4_orphan_transaction_ids` | Supplied GA4 transaction without Jadzia order. |
| `insufficient_evidence` | Required source/event-level data was not supplied or does not yet exist. |

## Remaining REV-R0-02 gates

1. Wizard/ZZPackage emits canonical GA4 `transaction_id={order_id}`.
2. INT-002 carries explicit test/payment/attribution evidence.
3. Controlled E2E is classified `test` and excluded from KPI.
4. One verified real order matches WC, GA4, and Jadzia.
5. Reconciliation test window has zero unresolved normalized duplicates.

Production deploy and data apply remain manual.
