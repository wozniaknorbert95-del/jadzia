# CLOSE — COI-OPS-AI-01 PASS (≥60% ops AI)

**Date:** 2026-07-18  
**Gate:** `COI-OPS-AI-01` — **completed**  
**PASS tip (measure):** `d97939a`  
**VPS tip after CLOSE docs:** (ff after this commit)  
**Ratio:** **20 / 33 = 60.6%** (v1.1)  
**GO deploy:** explicit in-session

## Verify

| Check | Result |
|-------|--------|
| Deploy tip | `d97939a` ff from `8de8806` |
| Backup | `jadzia-pre-rev-demand-01-20260718-154141.db` integrity `ok` |
| `jadzia.service` | active |
| `/health` | OK |
| Widget `created_at` | present; 7 rows 14d |
| `RATIO_V11` | **60.6% PASS_GE_60 YES** |
| CRITICAL HITL | queue markers retained (disposition/available_actions) |
| Scorecard #9 | **LIVE / PASS** |

## DONE

1. Commit+push instrumentacji (`feat(ops-ai): widget created_at + v1.1 count`)
2. VPS deploy via `rev-demand-01-deploy-vps.sh` @ `d97939a`
3. Schema migrate: `widget_chat_sessions.created_at` + backfill
4. Fresh SQL count → **60.6%**
5. Scorecard + todo `COI-OPS-AI-01` **completed**

## Numbers

| Contract | AI | Human | Ratio |
|----------|---:|------:|------:|
| v1 (history) | 11 | 13 | 45.8% |
| **v1.1 PASS** | **20** | **13** | **60.6%** |

AI breakdown: tickets brief+cs_followup=8, leads=5, widget=7.

## LEFT

- **Next gate:** `COI-PM-01` (OS Mission Control ritual) — `@blast`
- Gate D — **parked** (budget)
- Widget CTA smoke `reply_ok False` — pre-existing / env, nie blocker OPS-AI
- worker `/worker/health` may show `ssh_connection: error` transient — SQLite OK

## RISKS / DON'T

- Nie fałszuj AI vs human publish
- Nie auto-CRITICAL / nie Gate D bez GO+budget
- Nie commit `_mint_*` / `_recover_*`

## NEXT_SESSION

`@blast COI-PM-01` — PM ritual (Agent OS HITL), nie OPS-AI.
