# Handoff — MB eval-pack v2 LIVE + weekly nudge

**Date:** 2026-07-19  
**Gate:** MKT-BRAIN-PRO  
**Status:** EVAL V2 LIVE tip `bec2b90`; weekly nudge shipping in follow-up tip

## Deploy evidence (bec2b90)

```
tip=bec2b90
health OK
accuracy None n 0 gate False no_scores   # expected until Dowódca scores
pack v2_stratified n 3
marketing_shadow_eval present
=== EVAL_V2_DEPLOY_OK ===
```

## Human next

Telegram: `/mb_eval` → score agree/partial/disagree until n≥20 and accuracy≥70% / 14d.

## Agent follow-up

Weekly durable nudge: `run_eval_nudge_if_due` + `MARKETING_EVAL_PUSH_INTERVAL_SECONDS=604800`.
