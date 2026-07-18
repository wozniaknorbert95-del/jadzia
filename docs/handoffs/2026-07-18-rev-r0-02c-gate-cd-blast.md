# BLAST — REV-R0-02C Gate C/D controlled E2E

**Date:** 2026-07-18  
**Backlog ID:** `REV-R0-02C`  
**Checklist:** `zzpackage.flexgrafik.nl/docs/checklists/REV-R0-02C-controlled-e2e.md`  
**Prior close:** `docs/handoffs/2026-07-18-rev-r0-02-session-CLOSE.md`  
**Code change in this session:** NONE (execution only)

---

## B — Background

Revenue Truth producers/consumers are LIVE. Remaining work is controlled proof that:
1. Mollie **test** payment → Jadzia `classification=test`, no GA4 `purchase`, `kpi_paid_eligible=false`
2. One Dowódca-authorized **real** paid order → WC ↔ Jadzia ↔ GA4 reconcile

**Flow:** Wizard UTM → WC order + Mollie → INT-002 v2 webhook → Jadzia SQLite → GA4 DebugView / reconcile dry-run

| Layer | Commit / artifact |
|-------|-------------------|
| Jadzia VPS | `504fdf6` (`feat/rev-r0-02c-int002-consumer`) |
| zzpackage producer | `bfe8485` LIVE; ops helper `ac408c6` |
| wp-config | `FG_REVENUE_ENVIRONMENT=production` |

---

## L — Limitations & hard stops

- No GA4 history replay.
- No `--apply-classifications` without Dowódca review of dry-run.
- No delete of leads/orders (classification append-only).
- No R1, B3-2, TikTok, BFG.
- No synthetic live charge for Gate D — Dowódca-authorized genuine paid order only.
- Stop if Mollie mode cannot be confirmed `test` (Gate C) or `live` (Gate D).
- No secrets / customer PII in evidence, chat, or handoffs.
- Evidence directory is operator-local **outside Git**.

---

## A — Execution plan (no code)

- [ ] Preflight: VPS `504fdf6`, service active, backup present, v2 columns present
- [ ] Gate A/B: treat as PASS from prior session; record commits in `01-preflight.txt`
- [ ] Gate C: browser Wizard with UTM params → cart ≥ €199 → Mollie test → redacted WC/Jadzia/GA4/reconcile
- [ ] Gate D: wait for Dowódca auth + one real order → redacted WC/Jadzia/GA4/final reconcile
- [ ] Closeout: PII-free proof handoff; merge PR #3 + #74 only after Gate D PASS

---

## S — Success criteria

### Gate C
- [ ] `_mollie_payment_mode = test`
- [ ] Jadzia: `schema_version=int-002.v2`, `classification=test`, `is_test=true`, `test_reason=mollie_test_mode`
- [ ] GA4 DebugView: **no** `purchase` for controlled order
- [ ] Reconcile dry-run: `kpi_paid_eligible=false`, no normalized duplicate, no history mutation

### Gate D
- [ ] Mollie `live`, gross ≥ €199, `classification=real`, attribution known/partial
- [ ] GA4 `transaction_id` = bare WC order ID; `payment_status=paid`, `is_test=false`
- [ ] Final reconcile: test excluded, real KPI-eligible, zero unresolved duplicates/orphans/missing in proof window

---

## T — Test / proof plan

| Step | Method |
|------|--------|
| Preflight | SSH VPS health + SQLite column/event check |
| Gate C cart | Browser: `/wizard/?utm_…&wizard_link_id=e2e-r0-02c` |
| WC meta | Redacted order meta export (no order key / PII) |
| Jadzia | Read-only SQL by `order_id` |
| GA4 | DebugView screenshot (no PII) |
| Reconcile | `revenue_reconcile.py` dry-run with transaction ID JSON only |

Evidence root (outside Git): `REV-R0-02C/` per checklist.

---

```text
BLAST_ANCHOR: docs/handoffs/2026-07-18-rev-r0-02c-gate-cd-blast.md
BACKLOG_ID: REV-R0-02C
INVARIANTS_TO_PROTECT: no GA4 replay; no apply-classifications without review; append-only classification; no R1/B3-2/TikTok/BFG
SUCCESS_CRITERIA: controlled test excluded + one authorized real attributable order reconciled
IMPLEMENTATION_PLAN: preflight → Gate C Mollie test → Gate D Dowódca real → closeout/merge

---
CURRENT_STAGE: Mollie TEST CONFIRMED — awaiting GO for Gate C paid
RECOMMENDED_NEXT: full Gate C paid Mollie TEST (after Dowódca GO)
WHY_NEXT: Test mode verified on www.mollie.com; smoke used failed status only.
PROOF: docs/handoffs/2026-07-18-rev-r0-02c-mollie-test-READY.md
---
```

