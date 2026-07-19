# Handoff — REV-R0-02C deploy execution

**Date:** 2026-07-17  
**Operator approval:** explicit Dowódca deploy (`masz wykonac deploy !!`)  
**Status:** CONSUMER + PRODUCER DEPLOYED / E2E PENDING

## Git deploy order (canonical)

| Step | Repo | Branch | Commit | Action |
|------|------|--------|--------|--------|
| 1 | `jadzia-core` | `feat/rev-r0-02c-int002-consumer` | `f266e30` | VPS deploy first |
| 2 | `zzpackage` | `feat/rev-r0-02b-revenue-producers` | `bfe8485` | GHA production deploy second |
| 3 | zzpackage wp-config | — | — | `FG_REVENUE_ENVIRONMENT=production` |

Branches remain feature branches until PR/merge to `master`.

## Jadzia consumer (VPS 185.243.54.115)

- SQLite backup: `/opt/jadzia/data/jadzia-pre-int002-v2-20260717-222331.db` (`integrity_check=ok`)
- Checked out: `feat/rev-r0-02c-int002-consumer` @ `f266e30`
- Service: `jadzia.service` active after restart
- Schema: v2 columns + `idx_orders_checkout_id` present
- Prod smoke: **7 pass / 1 fail** (`analytics/snapshot` — pre-existing, outside INT-002 slice)
- INT-002 compatibility smoke:
  - v1 payload → HTTP 200, `schema_version=int-002.v1`
  - v2 test payload → HTTP 200, `schema_version=int-002.v2`, `classification=test`

## zzpackage producer (Cyber-Folks)

- GHA: [Production Deploy run 29611075777](https://github.com/wozniaknorbert95-del/zzpackage/actions/runs/29611075777) — **SUCCESS**
- Ref: `feat/rev-r0-02b-revenue-producers` @ `bfe8485`
- Theme on prod contains:
  - `page-bedankt.php` canonical `transaction_id` + paid/test gating
  - `fg-jadzia-order-webhook.php` with `schema_version: int-002.v2`
- wp-config backup + define added:
  - `FG_REVENUE_ENVIRONMENT=production`
  - backup: `wp-config.php.bak-rev-r0-02c-*`

## Still open (gate closure)

1. **Controlled Mollie test E2E** — `zzpackage/docs/checklists/REV-R0-02C-controlled-e2e.md`
   - test order → Jadzia `classification=test`, no GA4 purchase
   - one authorized real paid order → WC ↔ Jadzia ↔ GA4 reconcile
2. **REV-R0-02A** — classification/reconciliation code not integrated in jadzia-core; blocks full REV-R0-02 closeout
3. **PR/merge** — feature branches → `master` after Dowódca review

## Safety notes

- No historical GA4 purchase replay
- Deploy order respected: consumer before producer
- No R1, B3-2, TikTok, BFG touched

```text
STATE: REV-R0-02C deploy executed
DEPLOY_STATE: PROD LIVE — E2E + 02A integration pending
NEXT: controlled Mollie E2E + merge PRs
SESSION_VERDICT: DEPLOY_SUCCESS_WITH_E2E_PENDING
```
