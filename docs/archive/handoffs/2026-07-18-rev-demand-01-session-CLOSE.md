# Handoff — REV-DEMAND-01 session CLOSE (F0–F4 + VPS deploy)

**Date:** 2026-07-18  
**Repo:** jadzia-core  
**Branch:** `master` @ **`3746f9e`** (local = origin)  
**VPS:** `/opt/jadzia` @ **`3746f9e`**, `jadzia.service` **active**  
**Backup:** `/opt/jadzia/data/jadzia-pre-rev-demand-01-20260718-090629.db` (integrity ok)  
**Status:** SUCCESS  
**Session verdict:** SUCCESS  
**Owner:** Revenue / Demand senior slice

## DONE

### Program REV-DEMAND-01 (F0–F4)
| Phase | ID | Result |
|-------|-----|--------|
| F0 | SSoT register | PASS — Demand track + parks preserved |
| F1 | 01a dogfood | PASS (tests + post-deploy smoke path) |
| F2 | 01b widget CTA | PASS code — fields `wizard_deeplink` / `cta_sku` / `lead_id` |
| F3 | 01c disposition | PASS — column + API + Commander UI |
| F4 | playbook | PASS — `docs/ops/JADZIA-REVENUE-DOGFOOD.md` |

### Deploy (Dowódca-authorized)
- Switched VPS from stale feature tip → `master` @ `3746f9e`
- `leads.disposition` column present after restart
- Health: `degraded` (WP SSH probe error — **pre-existing**, sqlite + worker OK)
- Widget response schema LIVE (keys include CTA fields)

### Prior in same era (not this slice)
- REV-R0 Gate C PASS; Gate D parked (no budget)
- COI A+ strategy HITL; no-ask rule
- PR jadzia #3 + zzpackage #74 merged earlier

## LEFT (ordered — next session)

1. **P0 hotfix (1-1-1):** Widget CTA uses `LeadScorer` score only → AI `lead.score=65` / intent high still yielded `wizard_deeplink=null` when scorer=30. Fix: CTA when `max(ai_score, lead_score) >= 40` OR `intent == high` (from either source). Test + redeploy.
2. **REV-DEMAND-02:** Widget session durability (SQLite/TTL hybrid) — after CTA hotfix.
3. **REV-DEMAND-03 / 04:** pending (INSPIRE→lead; brief→sales HITL).
4. Human parks unchanged: Gate D, S1-01, OPS-FB-HYGIENE-01, B3-*, TikTok, D1-03.

## CRITICAL WARNINGS

- **No Gate D / Mollie LIVE / min199 change / live charge.**
- **Do not delete parked todos** to “clean” backlog.
- **Do not ship** `deployment/_recover_rev_r0_02a.py`.
- Deploy script `deployment/rev-demand-01-deploy-vps.sh` — keep LF endings on VPS.
- CI lint (design-agent scope) still red on master historically; Tests workflow green for Demand commit.
- Health `ssh_connection=error` ≠ Demand failure; do not chase unless WP SSH ops needed.
- One `active_gate` only.

## Active / parks registry

**Active:** `REV-DEMAND-02` (next) — start with CTA P0 then durability.  
**Parks:** `REV-R0-02C` gate_d_deferred | `S1-01` blocked | `OPS-FB-HYGIENE-01` ready_for_human | `B3-*` deferred | `C1-01` parked | `D1-03` deferred.

## Evidence / docs

- Close: `docs/handoffs/2026-07-18-rev-demand-01-CLOSE.md`
- Dogfood ops: `docs/ops/JADZIA-REVENUE-DOGFOOD.md`
- This file: session + deploy truth

## NEXT SESSION START

```text
@blast REV-DEMAND-02a widget CTA score hotfix

Repo: jadzia-core ONLY
Branch: master @ 3746f9e (VPS same)
Cel: 1-1-1 — CTA when max(AI lead.score, LeadScorer) >= 40 OR intent high; tests; Dowódca-authorized redeploy
STOP: bez Gate D; bez Mollie; bez session-durability w tym samym PR; bez kasowania parków
Handoff: docs/handoffs/2026-07-18-rev-demand-01-session-CLOSE.md
Then: REV-DEMAND-02 session durability
```

```text
STATE: Demand-01 LIVE on VPS 3746f9e; CTA scorer gap known; Gate D parked
DEPLOY_STATE: Jadzia master 3746f9e active; backup 20260718-090629
NEXT: @blast REV-DEMAND-02a CTA hotfix → then 02 durability
SESSION_VERDICT: SUCCESS
```
