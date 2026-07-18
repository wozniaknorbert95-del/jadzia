# Handoff — REV-R0-02C Mollie TEST READY

**Date:** 2026-07-18  
**Prior:** `docs/handoffs/2026-07-18-rev-r0-02c-gate-c-HARD-STOP.md`  
**Status:** `MOLLIE_TEST_CONFIRMED` — Gate C can resume on GO  
**Session verdict:** SUCCESS

## DONE

### Mollie TEST enabled
- WP option `mollie-payments-for-woocommerce_test_mode_enabled` → **yes** (WP-CLI on CyberFolks)
- Cache flushed (WP object cache + LiteSpeed purge)
- WP Admin confirm (logged in):
  - Banner: “The test mode is active…”
  - “Successfully connected with Test API”
  - Payment mode dropdown: **Test API**
- Test API key: present (masked); Live API key: present (masked)
- iDEAL gateway: enabled
- `FG_REVENUE_ENVIRONMENT`: **not changed** (stays production; Mollie test wins classification)

### Smoke verification (NOT full Gate C)
- Wizard → checkout → Mollie iDEAL
- Redirect host: **`www.mollie.com`** (not `pay.ideal.nl`)
- Banner: “Let op: dit is een testmode-betaling.”
- Test status page present: Open / Betaald / Mislukt / Geannuleerd / Verlopen
- Smoke action: **Mislukt** (failed) — deliberately not paid
- WC order_id for smoke only: **3208** (unpaid/failed; not Gate C proof)

### Evidence (outside Git)
- `Documents/REV-R0-02C/10-mollie-test-mode-ON.txt`
- `Documents/REV-R0-02C/11-mollie-test-ui-CONFIRMED.txt`

## NOT DONE (next session after GO)

1. Full Gate C: one Mollie TEST **paid** order ≥ €199 with UTM `e2e-r0-02c`
2. Proof: WC `_mollie_payment_mode=test` → Jadzia `classification=test` / `test_reason=mollie_test_mode` → no GA4 purchase → reconcile `kpi_paid_eligible=false`
3. Dowódca returns Mollie to **LIVE** before Gate D
4. Gate D: one authorized real order
5. Merge PR #3 (jadzia) + #74 (zzpackage)

## SAFETY

- No live charge
- No GA4 history replay
- No `--apply-classifications`
- No R1 / B3-2 / TikTok / BFG
- No secrets / API keys / order keys in this handoff

## Ops note

Mollie remains in **TEST** until Gate C PASS. Dowódca switches back to LIVE before Gate D.

```text
STATE: MOLLIE_TEST_CONFIRMED — ready to resume Gate C
DEPLOY_STATE: Jadzia 504fdf6 LIVE; producer bfe8485 LIVE; Mollie TEST ON
NEXT: @blast Gate C paid Mollie TEST (after Dowódca GO)
SESSION_VERDICT: SUCCESS
```
