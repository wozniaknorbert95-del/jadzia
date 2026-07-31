---
status: "[CLOSED]"
title: "VF-VHQ-DI-S4-SNR-FINISH — CLOSED+DEPLOY PASS"
updated: "2026-07-31"
gate: "VF-VHQ-DI-S4-SNR-FINISH"
verdict: "CLOSED+DEPLOY PASS"
feature_tip: "35259b4"
prod_tip: "c56b13e"
cache: "vhq-w62a"
scorecard_dim: "S4 → 5"
evidence: "docs/handoffs/evidence-vhq-di-s4/"
deploy_close: "docs/handoffs/2026-07-31-DEPLOY-VHQ-DI-S4-00-CLOSE.md"
---

# CLOSE — VF-VHQ-DI-S4-SNR-FINISH

## Verdict

**CLOSED+DEPLOY PASS.** Tip **`c56b13e`** (feature **`35259b4`**) · cache **`vhq-w62a`**. Scorecard **S4 = 5/5**.

## Delivered

| Item | Result |
|------|--------|
| `analytics_stale` → INFO | DONE |
| Decide-now excludes GA4 stale | DONE (prod + VPS priorities) |
| Noise &lt;10% | **0%** (2/2 actionable) |
| pytest | 10/10 |
| Ops confidence line preserved | DONE |
| Order PARKED EV-W2-010 | preserved |
| Stub Decide-now | 0% |

## Prod dogfood

URL: `?v=vhq-w62a&vhq=mc`  
Decide-now: Case study 3149 · Sales CTA #10 — **no** Analytics stale.  
Ops: `OK · data confidence degraded (freshness red)`.  
VPS: `STALE_IN_PRIO False` · stale INFO in queue.  
Evidence: `docs/handoffs/evidence-vhq-di-s4/NOTES.md`

## Explicit non-actions

No S5 NBA · no Order LIVE · no 3D · no MKT · no Ads/Mollie

## Next

**`VF-VHQ-DI-S5-NBA`** — ranked next action card.
