# Handoff — REV-R0-02C Gate C HARD STOP (Mollie LIVE)

**Date:** 2026-07-18  
**Blast:** `docs/handoffs/2026-07-18-rev-r0-02c-gate-cd-blast.md`  
**Checklist:** `zzpackage.flexgrafik.nl/docs/checklists/REV-R0-02C-controlled-e2e.md`  
**Status:** GATE C BLOCKED — Mollie not in TEST mode  
**Session verdict:** HARD_STOP (no live charge completed)

## DONE

- BLAST anchor written (execution-only; no code change).
- Preflight PASS:
  - Jadzia VPS `/opt/jadzia` @ `504fdf6`, `jadzia.service` active, `/health` ok
  - Backup present: `jadzia-pre-rev-r0-02a-20260718-063000.db`
  - v2 order columns + `revenue_classification_events` present
- Gate C cart started in browser:
  - Wizard UTM: `utm_source=e2e&utm_medium=controlled&utm_campaign=rev-r0-02c&wizard_link_id=e2e-r0-02c`
  - Groeier preset cart **€882,00**
  - Synthetic identity (e2e-prefixed); no secrets in evidence
- Checkout submitted with Mollie iDEAL → redirected to **live** `pay.ideal.nl`
- Payment **aborted** (no bank selected, no charge)
- Operator evidence (outside Git): `Documents/REV-R0-02C/`

## HARD STOP

Checklist clause triggered:

> Mollie mode cannot be positively confirmed as `test` for the controlled test.

Observed:

| Check | Result |
|-------|--------|
| Host | `pay.ideal.nl` (live iDEAL / Wero) |
| Amount | €882,00 |
| Mollie test status buttons | **absent** |
| Bank selector | present (live) |
| Jadzia new paid row after attempt | **none** (top rows still prior smoke IDs) |

## NOT DONE

- Gate C: paid Mollie TEST → Jadzia `classification=test` / no GA4 purchase / reconcile
- Gate D: authorized real order
- PR merge #3 / #74 (still after Gate D PASS)

## REQUIRED HUMAN ACTION

1. Set WooCommerce Mollie plugin to **TEST** mode (test API keys).
2. Confirm test checkout shows Mollie test UI (paid/failed buttons), not `pay.ideal.nl` bank selector.
3. Resume Gate C with one Mollie TEST payment only.
4. Then Gate D only with Dowódca-authorized genuine live paid order.

## SAFETY (honored)

- No live charge completed
- No GA4 history replay
- No `--apply-classifications`
- No R1 / B3-2 / TikTok / BFG

```text
STATE: REV-R0-02C Gate C HARD STOP — Mollie LIVE on prod
DEPLOY_STATE: Jadzia 504fdf6 LIVE; producer bfe8485 LIVE (unchanged)
NEXT: Dowódca enables Mollie TEST → resume Gate C → Gate D → merge PRs
SESSION_VERDICT: HARD_STOP
```
