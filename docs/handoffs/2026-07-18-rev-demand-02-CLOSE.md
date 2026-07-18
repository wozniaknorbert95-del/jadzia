# Handoff — REV-DEMAND-02 Widget session durability

**Date:** 2026-07-18  
**Repo:** jadzia-core  
**Branch:** `master` (deploy in progress / see tip after GO)  
**Status:** CODE+TESTS VERIFIED — GO authorized  
**Owner:** Revenue / Demand senior slice

## DONE (pre-deploy)

| Item | Result |
|------|--------|
| Hybrid | L1 TTLCache + L2 `widget_chat_sessions` (TTL 24h) |
| Fix | session_id normalized to 128 chars for L1/L2 key parity |
| Tests | **15 passed** (durability + CTA + customer_chat) |
| Verify | expire deletes row; cache-clear reloads from SQLite; save-fail soft |

## Deploy checklist (GO)

1. Commit (exclude `_recover_*.py`) + push
2. VPS: backup + pull + restart (`rev-demand-01-deploy-vps.sh`)
3. Smoke: table exists; turn1 → restart → turn2 same session keeps history

## STOP / parks

No Gate D / Mollie / min199. Parks untouched. No `_recover_*` ship.

## Next

**REV-DEMAND-03** INSPIRE → lead bridge (consent) after 02 LIVE.
