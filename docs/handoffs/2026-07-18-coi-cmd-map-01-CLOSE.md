# Handoff — COI-CMD-MAP-01 System map prod deep-links

**Date:** 2026-07-18  
**Repo:** jadzia-core ONLY  
**FEATURE_SHA:** *(set at commit)*  
**TIP_SHA:** *(set after deploy)*  
**VPS:** `/opt/jadzia`  
**Status:** SUCCESS (implement; deploy in-session)  
**Session verdict:** SUCCESS  
**Owner:** Control plane / Commander

## DONE

| Item | Result |
|------|--------|
| ADR D0.6 | Canonical URLs → `os.flexgrafik.nl` + `cmd.flexgrafik.nl` (+ docs `/docs/`); hosted-runtime note |
| Home system map | Agent OS + VCMS + VCMS docs deep-links; localhost removed |
| Settings list | Same prod URLs (read-only) |
| Agents tab | Still `https://os.flexgrafik.nl` (`noopener noreferrer`) — no localhost regress |
| Scope | jadzia-core only; no Agent OS / VCMS merge; no Nginx/Basic Auth changes |

## DoD (verify)

- [ ] Phone/desktop: Home → Agent OS → `os.flexgrafik.nl` (Basic Auth OK)
- [ ] Home → VCMS → `cmd.flexgrafik.nl`
- [ ] Settings lista zgodna z Home
- [ ] ADR nie traktuje VCMS jako „nie runtime” / Agent OS tylko localhost jako prod

## CRITICAL WARNINGS

- Gate D / parks / `_recover_*.py` — untouched
- No SSO between Basic Auth realms
- Configurable map URLs in SQLite — out of scope (future)

## NEXT

```text
STATE: MAP-01 ready_for_deploy
NEXT: push master → VPS tip pull/restart → human phone tap verify
```
