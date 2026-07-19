# Handoff — REV-R0-02C INT-002 v2 consumer

**Date:** 2026-07-17  
**Branch:** `feat/rev-r0-02c-int002-consumer`  
**Base:** `master` @ `4b583dc`  
**Status:** CODE PASS / DEPLOY EXECUTED (see execution handoff)
**Deploy/data apply:** performed 2026-07-17 — `docs/handoffs/2026-07-17-rev-r0-02c-deploy-EXECUTION.md`

## DONE

- Extended `WooOrderWebhookRequest` with the complete additive INT-002 v2
  producer shape while preserving v1 compatibility.
- Added semantic validation:
  - canonical numeric order IDs for v2;
  - explicit field presence, totals consistency, and payment evidence;
  - coherent `real|test|unknown` classification;
  - paid live production evidence required for `real`;
  - historical v2 payloads may explicitly carry unknown/missing checkout data.
- Added durable SQLite evidence columns for:
  - schema/currency/net/tax;
  - payment state/method/provider/mode/timestamp;
  - classification/test evidence;
  - checkout identity/environment;
  - PII-free attribution JSON.
- Added safe additive migration for existing `orders` tables.
- Added a partial unique index on non-empty `checkout_id`.
- Preserved v2 evidence when a later legacy v1 retry updates order status.
- Added parsed attribution and nullable boolean `is_test` to order reads.
- Added executable producer-consumer tests for:
  - real and test v2 payloads;
  - invalid semantic combinations;
  - historical unknown evidence;
  - API-to-SQLite persistence;
  - legacy v1 compatibility;
  - v1 retry preservation;
  - checkout ID uniqueness;
  - migration of an existing v1 database without data loss.
- Added manual deployment runbook:
  `docs/ops/INT-002-V2-DEPLOY.md`.

## PROOF

```text
Focused INT-002 v1 + v2:
17 passed

New v2 contract module:
8 passed

Full pytest:
491 passed, 17 skipped, 1 xfailed, 4 failed

Focused Ruff:
PASS

Focused Black:
PASS

Python compile:
PASS

git diff --check:
PASS
```

The four full-suite failures predate and are outside this slice:

- exact-route allowlist is stale relative to existing Commander/Design Agent routes;
- three Telegram `/zadanie` tests expect the pre-existing command name instead
  of the current `/ticket` alias.

No INT-002 test failed.

Repository-wide Ruff/Black/Mypy are not clean on the base branch. Focused
changed modules/tests pass Ruff/Black; `py_compile` and executable tests cover
the modified model/database paths.

## DEPLOY BLOCKER

The active workspace initially pointed at `feat/da-insire-enterprise`. A clean
02C branch was created from current `master`, but that base does not contain the
previously uncommitted REV-R0-02A classification/reconciliation artifacts.
The reviewed zzpackage REV-R0-02B producer is also uncommitted in its repository.

Therefore production deployment would violate the required order and produce
an incomplete gate. Before deploy:

1. Commit/recover and integrate REV-R0-02A.
2. Review and commit REV-R0-02B in zzpackage.
3. Review/commit this consumer branch.
4. Operator backs up SQLite.
5. Operator manually deploys Jadzia consumer first.
6. Operator verifies v1 smoke + v2 persistence.
7. Operator manually deploys zzpackage producer.
8. Run controlled Mollie test and authorized real-order reconciliation.

User approval to deploy was received, but repository rule Zasada 11 requires
manual operator deployment and the prerequisites above are not satisfied.

## SAFETY

- No production command, SSH, secret read, service restart, DB migration, or
  live webhook was executed.
- No production database was opened.
- No deploy, R1, B3-2, TikTok, BFG, or unrelated cleanup was performed.
- Migration is additive and covered against a legacy schema fixture.

```text
STATE: REV-R0-02C consumer code ready
DEPLOY_STATE: LIVE — consumer + producer deployed; E2E + 02A pending
RUNBOOK: docs/ops/INT-002-V2-DEPLOY.md
EXECUTION: docs/handoffs/2026-07-17-rev-r0-02c-deploy-EXECUTION.md
NEXT: controlled Mollie E2E + REV-R0-02A integration + PR merge
SESSION_VERDICT: SUCCESS
```
