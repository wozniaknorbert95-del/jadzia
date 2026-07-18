# Handoff — REV-DEMAND-02a Widget CTA score hotfix

**Date:** 2026-07-18  
**Repo:** jadzia-core  
**Branch:** `master` (local tip was `b0fdd17` docs; code change uncommitted until Dowódca commits/GO)  
**VPS:** `/opt/jadzia` still **`3746f9e`** (Demand-01) — **not redeployed**  
**Status:** CODE+TESTS DONE — **await GO** for redeploy  
**Session verdict:** SUCCESS (implementation) / BLOCKED_DEPLOY (Zasada 11)  
**Owner:** Revenue / Demand senior slice

## DONE

| Item | Result |
|------|--------|
| BLAST | `docs/handoffs/2026-07-18-rev-demand-02a-BLAST.md` |
| CTA gate | `max(AI lead.score, LeadScorer) >= 40` OR either intent `high` |
| File | `agent/customer_agent.py` — `_cta_effective_score`, `_cta_intent_is_high`, call-site fix |
| Tests | `tests/unit/test_widget_demand_cta.py` — **8 passed** (incl. AI 65/high vs scorer 30) |
| Backlog | `REV-DEMAND-02a` → `ready_for_deploy` |

### Bug fixed
Previously: `score = lead_score or ai_score` → scorer `30` hid AI `65`; scorer intent overwrote AI `high`.  
Now: effective score = max; intent high from either source.

## LEFT

1. **Human GO:** commit (if desired) + redeploy VPS via `deployment/rev-demand-01-deploy-vps.sh` (or equivalent pull+restart).
2. **Smoke post-deploy:** widget path — AI mid/high lead → `wizard_deeplink` non-null even if scorer ~30.
3. **REV-DEMAND-02:** session durability (SQLite/TTL) — **after** 02a LIVE (1-1-1, not same PR).

## CRITICAL WARNINGS

- **No Gate D / Mollie LIVE / min199 / live charge.**
- **Do not delete parked todos.**
- **Do not ship** `deployment/_recover_rev_r0_02a.py` (untracked — leave out of commit).
- Health `ssh_connection=error` pre-existing — ignore unless WP SSH needed.

## Active / parks

**Active:** `REV-DEMAND-02a` (ready_for_deploy)  
**Next after LIVE:** `REV-DEMAND-02` durability  
**Parks:** unchanged (Gate D, S1-01, OPS-FB-HYGIENE-01, B3-*, TikTok, D1-03)

## NEXT SESSION / GO blast

```text
@blast REV-DEMAND-02a GO redeploy → then REV-DEMAND-02 durability

Repo: jadzia-core ONLY
Cel: Dowódca GO → commit (exclude _recover_*) → VPS pull/restart → smoke CTA
Then: REV-DEMAND-02 widget session durability (1-1-1)
STOP: bez Gate D; bez Mollie; bez kasowania parków
```

```text
STATE: 02a code+tests green; VPS still Demand-01 3746f9e
DEPLOY_STATE: awaiting Dowódca GO
NEXT: GO redeploy 02a → then @blast REV-DEMAND-02 durability
SESSION_VERDICT: SUCCESS (code) / ready_for_human (deploy)
```
