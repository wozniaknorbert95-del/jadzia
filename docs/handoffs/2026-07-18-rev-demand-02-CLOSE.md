# Handoff — REV-DEMAND-02 Widget session durability

**Date:** 2026-07-18  
**Repo:** jadzia-core  
**Branch:** `master` @ **`60635e8`** (local = origin = VPS)  
**VPS:** `/opt/jadzia` @ **`60635e8`**, `jadzia.service` **active**  
**Backup:** `/opt/jadzia/data/jadzia-pre-rev-demand-01-20260718-095618.db` (integrity ok)  
**Status:** SUCCESS — LIVE  
**Session verdict:** SUCCESS  
**Owner:** Revenue / Demand senior slice

## DONE

| Item | Result |
|------|--------|
| Hybrid | L1 TTLCache + L2 `widget_chat_sessions` (TTL 24h) |
| Fix | session_id normalized ≤128 for L1/L2 parity |
| Tests | 15 passed local |
| Deploy | `60635e8`; table present; CTA smoke deeplink True |
| Restart proof | turn1 ALPHA → restart → turn2 BETA; SQLite has both (`msg_count=4`) |
| Backlog | `REV-DEMAND-02` **completed**; `active_gate` → `REV-DEMAND-03` |

## LEFT

1. **REV-DEMAND-03:** INSPIRE → lead bridge (consent) — next 1-1-1
2. Optional dogfood playbook update

## CRITICAL WARNINGS

- No Gate D / Mollie LIVE / min199 / live charge
- Do not delete parks; do not ship `_recover_*.py`
- Health `ssh_connection=error` pre-existing

## NEXT SESSION START

```text
@blast REV-DEMAND-03 INSPIRE → lead bridge (consent)

Repo: jadzia-core ONLY | master @ 60635e8 (VPS same)
Cel: 1-1-1 — INSPIRE session → durable lead on email+consent
STOP: bez Gate D; bez Mollie; bez kasowania parków; bez _recover_*.py
Handoff: docs/handoffs/2026-07-18-rev-demand-02-CLOSE.md
```

```text
STATE: Demand-02 LIVE on VPS 60635e8; widget history survives restart
DEPLOY_STATE: Jadzia master 60635e8 active; backup 20260718-095618
NEXT: @blast REV-DEMAND-03 INSPIRE→lead
SESSION_VERDICT: SUCCESS
```
