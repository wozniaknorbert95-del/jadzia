# Handoff — REV-DEMAND-02a Widget CTA score hotfix

**Date:** 2026-07-18  
**Repo:** jadzia-core  
**Branch:** `master` @ **`68e09bb`** (local = origin = VPS)  
**VPS:** `/opt/jadzia` @ **`68e09bb`**, `jadzia.service` **active**  
**Backup:** `/opt/jadzia/data/jadzia-pre-rev-demand-01-20260718-092153.db` (integrity ok)  
**Status:** SUCCESS — LIVE  
**Session verdict:** SUCCESS  
**Owner:** Revenue / Demand senior slice

## DONE

| Item | Result |
|------|--------|
| CTA gate | `max(AI lead.score, LeadScorer) >= 40` OR either intent `high` |
| Code | `agent/customer_agent.py` |
| Tests | `tests/unit/test_widget_demand_cta.py` — 8 passed |
| Commit | `68e09bb` pushed to `origin/master` |
| Deploy | VPS pull+restart; smoke `has_deeplink True`, `cta_sku CS-SET-PRO-ZZP` |
| Backlog | `REV-DEMAND-02a` → **completed**; `active_gate` → `REV-DEMAND-02` |

## LEFT

1. **REV-DEMAND-02:** Widget session durability (SQLite/TTL hybrid) — next 1-1-1.
2. Optional dogfood playbook.

## CRITICAL WARNINGS

- **No Gate D / Mollie LIVE / min199 / live charge.**
- **Do not delete parked todos.**
- **Do not ship** `deployment/_recover_rev_r0_02a.py`.
- Health `ssh_connection=error` pre-existing — ignore unless WP SSH needed.

## Active / parks

**Active:** `REV-DEMAND-02` (durability)  
**Parks:** unchanged (Gate D, S1-01, OPS-FB-HYGIENE-01, B3-*, TikTok, D1-03)

## NEXT SESSION START

```text
@blast REV-DEMAND-02 widget session durability

Repo: jadzia-core ONLY | master @ 68e09bb (VPS same)
Cel: 1-1-1 — SQLite/TTL hybrid session durability for widget chat
STOP: bez Gate D; bez Mollie; bez kasowania parków; bez _recover_*.py
Handoff: docs/handoffs/2026-07-18-rev-demand-02a-CLOSE.md
```

```text
STATE: Demand-02a LIVE on VPS 68e09bb; CTA max/intent fixed
DEPLOY_STATE: Jadzia master 68e09bb active; backup 20260718-092153
NEXT: @blast REV-DEMAND-02 session durability
SESSION_VERDICT: SUCCESS
```
