# CLOSE — Sequence deploy + verify (post KNOW-01)

**Date:** 2026-07-18  
**Jadzia tip:** `b3824e5`  
**VCMS tip (git):** `8fba568` (PR #20 + #21)  
**VCMS runtime:** `pm2 vcms-core` **online** @ `:8001`

## Deploy done

| Step | Result |
|------|--------|
| VCMS Node was down | Restored — `pm2` online, `/health` `{"status":"OK"}` |
| VitePress dist + KNOW page | LIVE under **`/docs/ecosystem/ai-os-knowledge`** (200 localhost) |
| Public cmd | **401** Basic Auth (expected) for `/docs/...` |
| Index home link | Fixed to `/docs/...` prefix (PR [#21](https://github.com/wozniaknorbert95-del/Flex-vcms/pull/21) merged) |
| Jadzia pull | `b3824e5` KNOW-01 CLOSE + scorecard #2 LIVE |
| Meta pointer | present on `bouwplaats-chaos` main |

## Verify matrix

| Check | Expected | Observed |
|-------|----------|----------|
| Jadzia tip | ≥ KNOW tip | `b3824e5` |
| Knowledge index status | LIVE | LIVE (COI-KNOW-01) |
| Scorecard #1 Dashboard | LIVE | LIVE |
| Scorecard #2 Wiedza | LIVE | LIVE |
| Scorecard #6 CS | LIVE | LIVE |
| Scorecard #9 OPS-AI | FAIL / in_progress | still **45.8%** (not re-measured this step) |
| VCMS health | OK | OK |
| KNOW HTML | 200 local / 401 public | PASS |
| Commander | 200 | 200 |
| Agent OS | 401 Basic Auth | 401 |

## Residual

- Full `Deploy-VPS.ps1` recursive `scp` hangs on this Windows host — lean **tar+scp** path used (document in VCMS runbook later).
- Widget CTA smoke on Jadzia deploy returned `reply_ok False` (pre-existing / env) — not KNOW blocker.
- Local VCMS WIP remains in `stash@{0}` (`scan-and-wip-after-deploy`).

## NEXT

See `docs/handoffs/2026-07-18-coi-ops-ai-01-BLAST.md` — **recommended path: OPS-AI-01 instrumentation → fresh ≥60% measure**.
