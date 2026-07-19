# Handoff — REV-R0-02C Gate D GO-pack (preflight locked)

**Date:** 2026-07-18  
**Owner:** Revenue senior slice (agent)  
**Status:** `GO_PACK_READY` — waiting Dowódca Mollie LIVE + Gate D authorize  
**Prior:** `2026-07-18-rev-r0-02c-READY-for-Gate-D.md`  
**Checklist:** `zzpackage/docs/checklists/REV-R0-02C-controlled-e2e.md`  
**Session verdict:** SUCCESS (no LIVE switch, no paid order)

## Decision (senior)

Next critical path is **not** more WP hygiene. COD is already OFF and checkout is iDEAL-only.  
The only remaining blocker before Gate D is **Mollie LIVE** (human-only).  
This pack freezes preflight so Gate D can start immediately after LIVE.

## Preflight LOCKED (2026-07-18)

| Check | Result |
|-------|--------|
| COD enabled | **no** |
| Available gateways | **iDEAL only** |
| Mollie test mode | **yes** (expected until Dowódca LIVE) |
| Test API key | present |
| Live API key | present |
| `FG_REVENUE_ENVIRONMENT` | `production` |
| Webhook URL / secret | defined |
| Jadzia consumer | `504fdf6` LIVE |
| Producer theme | `bfe8485` LIVE |
| Gate C proof | WC `#3209` test PASS |
| Order backlog | processing=31 (mostly stale COD — triage **after** Gate D) |

Evidence: `Documents/REV-R0-02C/21-gate-d-preflight.txt`

## Dowódca — Mollie LIVE (manual)

Do **not** ask the agent to flip LIVE.

1. WP Admin → WooCommerce → Mollie → Payment mode → **Live API**  
   (or equivalent; confirm connection banner is Live, not Test)
2. Confirm option `mollie-payments-for-woocommerce_test_mode_enabled` = **no**
3. Unpaid smoke `/afrekenen/`: still **iDEAL-only** (if Klarna/PayPal/etc. appear — stop and prune before Gate D)
4. Reply **GO Gate D** with authorization for exactly **1** real paid order ≥ €199

## Agent — Gate D execution (after GO)

```text
@blast REV-R0-02C Gate D LIVE paid order

Repo: jadzia-core + zzpackage
Cel: 1 real paid iDEAL ≥199; WC↔Jadzia↔GA4 reconcile proof
STOP: bez plugin updates; bez R1/TikTok/BFG; bez GA4 history replay; bez --apply-classifications
Handoff: docs/handoffs/2026-07-18-rev-r0-02c-gate-d-GO-pack.md
Checklist: zzpackage/docs/checklists/REV-R0-02C-controlled-e2e.md Gate D
Evidence: Documents/REV-R0-02C/06..09
```

### Proof targets (PASS = all true)

- WC: `processing`, `_mollie_payment_mode=live`, paid id + timestamp
- Jadzia: `schema_version=int-002.v2`, `classification=real`, `is_test=0`, 1 row
- Bedankt/GA4: `purchase` eligible (`payment_status=paid` && `is_test=false`)
- Reconcile dry-run: test `#3209` excluded; real order `kpi_paid_eligible=true`

### Explicit non-goals

- No plugin/core updates
- No Meta Pixel fix mid-gate
- No bulk cancel of 29 COD processing orders mid-gate
- No R1 / TikTok / BFG

## CLOSEOUT after Gate D PASS

1. Handoff Gate D PASS (PII-free)
2. Merge PR jadzia #3 + zzpackage #74
3. Mark `REV-R0-02` complete in `todo.json`
4. Schedule post-gate: COD backlog triage, `WP_DEBUG` off, Meta `is_test` gate, plugin updates

```text
STATE: COD OFF; iDEAL-only; Mollie TEST; Gate D GO-pack locked
DEPLOY_STATE: Jadzia 504fdf6; producer bfe8485; Gate C #3209 PASS
NEXT: Dowódca Mollie LIVE → GO Gate D
SESSION_VERDICT: SUCCESS
```
