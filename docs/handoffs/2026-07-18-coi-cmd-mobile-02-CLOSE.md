# Handoff — COI-CMD-MOBILE-02 Plan3 Control Surface

**Date:** 2026-07-18  
**Repo:** jadzia-core  
**FEATURE_SHA:** `abba339`  
**TIP_SHA:** `81347e8` (VPS SoT)  
**VPS:** `/opt/jadzia` @ `81347e8`, `jadzia.service` **active**  
**Backup:** `/opt/jadzia/data/jadzia-pre-rev-demand-01-20260718-130839.db` (ok)  
**Status:** SUCCESS — LIVE  
**Session verdict:** SUCCESS  
**Owner:** Control plane / Commander

## DONE

| Item | Result |
|------|--------|
| Enterprise login | One-time `code` (15 min) → `POST /auth/exchange` → JWT in localStorage (**no JWT in URL**) |
| TG | `/commander` (+ `/jwt`) for whitelist users |
| UI | bootstrap `?code=`, logout, auth status |
| PWA | `manifest.webmanifest` + `sw.js` (shell only) + icons 192/512 |
| Tests | `test_commander_session_login.py` **5 PASS** |
| Deploy | LIVE tip `81347e8`; VPS smoke **SMOKE_OK** (exchange 200, reuse 401, queue 200, PWA static 200) |
| BLAST | Amended for code-exchange (not rushed JWT-in-query) |

## LEFT (human)

1. Phone dogfood: TG `/commander` → Home → Ack `sales_cta` #4/#5
2. Optional: Add to Home Screen (Android Chrome)

## CRITICAL WARNINGS

- Gate D / parks / Agent OS merge — untouched
- Do not ship `_recover_*.py`
- Login link is single-use; do not forward TG message after open

## NEXT

```text
STATE: MOBILE-02 code ready_for_deploy
NEXT: Dowódca GO deploy → phone dogfood
```
