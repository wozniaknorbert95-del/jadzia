# Verify — pre-feature readiness (porządki)

**Date:** 2026-07-18  
**Repo:** jadzia-core  
**TIP_SHA (local=origin=VPS):** `447f8a6`  
**FEATURE Demand-04:** `51b3ef0`  
**Verdict:** **GO for next feature** (after Dowódca names it)  
**Session verdict:** SUCCESS  

## Checks

| Check | Result |
|-------|--------|
| Tip sync | local = origin = VPS `36417c0` |
| `jadzia.service` | **active** |
| Health | worker + sqlite OK; `ssh_connection=error` known |
| Smoke scripts on VPS | none leftover (`_smoke*` / `_cleanup*` clean) |
| Local dirty | only untracked `deployment/_recover_rev_r0_02a.py` (not shipped) |
| Unit tests | 20 PASS (`brief_node`, disposition, queue, widget CTA) |
| sales_cta dogfood | prior API PASS (ops-close) |
| Smoke leads | 3 leftover `@flexgrafik.test` disposition → **closed** this verify |
| Smoke sales tickets | already closed earlier; no new smoke tickets open |

## Queue snapshot (LIVE, post-cleanup)

| queue_type | count | Note |
|------------|------:|------|
| sales_cta | 2 | leads #4 `jan@bouw.com`, #5 `bob@gamil.com` — **kept** (real path; Dowódca HITL) |
| hot_lead | 2 | same band (high scores) |
| wp_ticket | 7 | ops / brief HITL — not wiped |
| publish_failed | 4 | marketing — not wiped this slice |
| fb_post_pending | 1 | not wiped |
| analytics_stale | 1 | known |

## SSoT

- `active_gate` = `NONE`
- Plan: `docs/handoffs/2026-07-18-ops-close-READY-next-feature.md`
- OPS-FB-HYGIENE-01 = **completed**
- Gate D / S1 / B3 / TikTok = **parked** (untouched)

## STOP (still)

- No Gate D / Mollie / min199 / live charge  
- No invent F8  
- No ship `_recover_*.py`  
- No Agent OS merge  

## NEXT

```text
STATE: tip 36417c0 verified; smoke cleaned; sales_cta for real leads #4/#5 intentional
NEXT: Dowódca GO names next feature (1-1-1)
```
