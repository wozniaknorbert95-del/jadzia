# Handoff — COI-CMD-MAP-01 System map prod deep-links

**Date:** 2026-07-18  
**Repo:** jadzia-core ONLY  
**FEATURE_SHA:** `d643b72`  
**TIP_SHA:** `d643b72` (VPS SoT)  
**VPS:** `/opt/jadzia` @ `d643b72`, `jadzia.service` **active**  
**Backup:** `/opt/jadzia/data/jadzia-pre-rev-demand-01-20260718-141316.db` (ok)  
**Status:** SUCCESS — LIVE  
**Session verdict:** SUCCESS  
**Owner:** Control plane / Commander

## DONE

| Item | Result |
|------|--------|
| ADR D0.6 | Canonical URLs → `os.flexgrafik.nl` + `cmd.flexgrafik.nl` (+ docs `/docs/`); hosted-runtime note |
| Home system map | Agent OS + VCMS + VCMS docs deep-links; localhost removed |
| Settings list | Same prod URLs (read-only) |
| Agents tab | Still `https://os.flexgrafik.nl` (`noopener noreferrer`) — no localhost regress |
| Deploy | LIVE tip `d643b72`; health active; widget CTA smoke OK |
| Scope | jadzia-core only; no Agent OS / VCMS merge; no Nginx/Basic Auth changes |

## LEFT (human)

1. Phone/desktop: Home → tap Agent OS → `os.flexgrafik.nl` (Basic Auth OK)
2. Tap VCMS → `cmd.flexgrafik.nl` (+ optional docs)
3. Settings lista zgodna z Home

## CRITICAL WARNINGS

- Gate D / parks / `_recover_*.py` — untouched
- No SSO between Basic Auth realms
- Configurable map URLs in SQLite — out of scope (future)

## NEXT

```text
STATE: MAP-01 LIVE
NEXT: human phone tap verify → idle (active_gate NONE)
```
