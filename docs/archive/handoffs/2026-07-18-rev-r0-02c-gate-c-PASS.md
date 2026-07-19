# Handoff — REV-R0-02C Gate C PASS

**Date:** 2026-07-18  
**Status:** GATE C PASS  
**WC order_id:** `3209`  
**Prior:** `docs/handoffs/2026-07-18-rev-r0-02c-mollie-test-READY.md`

## DONE — controlled Mollie TEST paid

### Flow
- Wizard UTM: `utm_source=e2e&utm_medium=controlled&utm_campaign=rev-r0-02c&wizard_link_id=e2e-r0-02c`
- Cart: Groeier **€882.00**
- Mollie TEST iDEAL → status **Betaald** (paid)
- Bedankt: `/bedankt/?order_id=3209` (order key not recorded)

### WooCommerce (redacted)
| Field | Value |
|-------|--------|
| status | `processing` |
| total | `882.00` EUR |
| payment_method | `mollie_wc_gateway_ideal` |
| `_mollie_payment_mode` | `test` |
| `_mollie_payment_id` | `tr_tuwYB***` |
| `_fg_revenue_checkout_id` | UUID `f1e83a96-22bc-43eb-9b70-be580b0ff158` |
| `_fg_revenue_checkout_started_at` | UTC `2026-07-18T05:18:09+00:00` |
| `_fg_revenue_checkout_environment` | `production` |
| attribution | last UTM e2e/controlled/rev-r0-02c + `wizard_link_id=e2e-r0-02c` |
| webhook | `_fg_jadzia_webhook_status=processing` |

### Jadzia INT-002
| Field | Value |
|-------|--------|
| schema_version | `int-002.v2` |
| payment_status | `paid` |
| payment_mode | `test` |
| classification | `test` |
| is_test | `1` |
| test_reason | `known_test_email_pattern` (e2e- email wins over mollie_test_mode; Mollie mode still `test`) |
| checkout_environment | `production` |
| rows | **1** (no duplicate) |
| attribution_status | `partial` (wizard_link_id present) |

### GA4
- Bedankt `dataLayer` **purchaseCount=0**
- `fg_get_order_details`: `is_test=true` → `purchaseWouldFire=false`
- Theme gates `gtag('event','purchase')` on `is_test === false`

### Reconcile (read-only)
- `mode=read_only`, `history_preserved=true`
- order `3209`: `classification=test`, **`kpi_paid_eligible=false`**
- `normalized_order_duplicates=0`
- `paid_orders_kpi_eligible=0`
- No `--apply-classifications`

### Evidence (outside Git)
`Documents/REV-R0-02C/` — `02` WC, `03` Jadzia, `04` GA4, `05` reconcile

## LEFT
1. Dowódca: Mollie → **LIVE** before Gate D
2. Gate D: one authorized real paid order
3. Merge PR #3 + #74 after Gate D PASS

## SAFETY
No live charge · no GA4 history replay · no apply-classifications · no R1/B3-2/TikTok/BFG

```text
STATE: REV-R0-02C Gate C PASS (order 3209 test / KPI excluded)
DEPLOY_STATE: Jadzia 504fdf6; producer bfe8485; Mollie still TEST
NEXT: Dowódca Mollie LIVE → Gate D → merge PRs
SESSION_VERDICT: GATE_C_PASS
```
