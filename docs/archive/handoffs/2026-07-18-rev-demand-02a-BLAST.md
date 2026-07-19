# BLAST — REV-DEMAND-02a Widget CTA score hotfix

**Date:** 2026-07-18  
**Repo:** jadzia-core  
**Branch:** master @ `b0fdd17` (Demand-01 LIVE VPS `3746f9e`)  
**Backlog:** `REV-DEMAND-02a`

## B — Background

Smoke: AI `lead.score=65` / `intent=high` + LeadScorer `30` → `wizard_deeplink=null`.  
Cause: CTA used `lead_score or ai_score` (first truthy scorer wins) and scorer overwrote intent.

## L — Limits

- No Gate D / Mollie / min199
- No session durability in this change
- No park deletes; do not ship `_recover_*.py`
- Redeploy only after Dowódca GO

## A — Actions

- [ ] `agent/customer_agent.py` — CTA gate: `max(ai_score, scorer_score) >= 40` OR either intent `high`
- [ ] `tests/unit/test_widget_demand_cta.py` — regression AI 65/high vs scorer 30
- [ ] Handoff + `todo.json` update; wait GO for VPS redeploy

## S — Success

- [ ] Scorer 30 + AI 65/high → deeplink present
- [ ] Either intent high → deeplink present
- [ ] Both low / scores < 40 → deeplink null
- [ ] `pytest tests/unit/test_widget_demand_cta.py` green

## T — Test plan

- Unit: `_should_attach_cta` + mocked `LeadScorer` regression
- Smoke post-GO: widget chat with high AI lead, confirm `wizard_deeplink` non-null

```text
BLAST_ANCHOR: docs/handoffs/2026-07-18-rev-demand-02a-BLAST.md
BACKLOG_ID: REV-DEMAND-02a
INVARIANTS_TO_PROTECT: parks, Gate D, no durability, no _recover ship
SUCCESS_CRITERIA: max/intent CTA + pytest green
---
CURRENT_STAGE: L1-Design → implement (senior decide, no-ask)
RECOMMENDED_NEXT: /implement
---
```
