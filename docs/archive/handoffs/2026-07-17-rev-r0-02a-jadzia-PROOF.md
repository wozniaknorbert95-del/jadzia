# Handoff — REV-R0-02A Jadzia classification and reconciliation

**Date:** 2026-07-17  
**Parent gate:** `REV-R0-02` (in progress)  
**Slice:** `REV-R0-02A` — jadzia-core only  
**Status:** PASS  
**Deploy/data apply:** not performed

## DONE

- Added append-only `revenue_classification_events`.
- Added deterministic `real|test|unknown` classification without raw PII evidence.
- Added canonical normalization for legacy GA4 `WC-{id}`.
- Added PII-free, read-only reconciliation report:
  - Jadzia ↔ supplied GA4 transaction IDs;
  - normalized duplicate detection;
  - KPI-paid eligibility;
  - explicit `insufficient_evidence` when event-level evidence is absent.
- Added explicit `--apply-classifications`; existing decisions are never overwritten.
- Added `classification`, nullable `is_test`, and reason to Commander order/lead reads.
- Excluded persisted `is_test=true` leads from Commander hot-lead queue.
- Disabled destructive E2E lead cleanup. Historical rows remain intact.
- Added runbook: `docs/ops/REVENUE-RECONCILIATION.md`.

## PROOF

```text
Focused revenue + compatibility:
22 passed

Ruff (new revenue files):
PASS

Black:
PASS

Mypy isolated revenue modules:
PASS

CLI:
python scripts/revenue_reconcile.py --help
PASS

Full tests:
492 passed, 17 skipped, 1 xfailed, 4 failed
```

The four full-suite failures are outside this slice:

- stale exact-route allowlist does not include existing Commander/Design Agent routes;
- three Telegram `/zadanie` expectations conflict with the existing `/ticket` alias behavior.

No changed revenue test failed.

## SAFETY

- No production database was available locally; no record was classified.
- No data was deleted.
- No production command, migration, or deploy was run.
- Production apply requires backup, dry-run review, and Dowódca approval.

## NEXT — separate repo/session

`REV-R0-02B` in `zzpackage.flexgrafik.nl` only:

1. Emit GA4 `transaction_id` equal to canonical WooCommerce `order_id`.
2. Preserve backward reconciliation for historical `WC-{id}`.
3. Extend INT-002 with explicit test/payment/attribution evidence compatibly.
4. Make checkout identity/test evidence durable enough for reconciliation.
5. Tests only; no deploy.

After 02B, return to `REV-R0-02C` for approved controlled E2E and one verified real-order proof.

```text
STATE_SYNC: todo.json + brain.md + AGENTS.md
HANDOFF_FILE: docs/handoffs/2026-07-17-rev-r0-02a-jadzia-PROOF.md
NEXT_SESSION_START: move to zzpackage.flexgrafik.nl → /blast REV-R0-02B
SESSION_VERDICT: SUCCESS
```
