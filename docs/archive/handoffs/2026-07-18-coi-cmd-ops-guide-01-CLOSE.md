# CLOSE — COI-CMD-OPS-GUIDE-01 (VCMS study ops handbook)

**Date:** 2026-07-18  
**Gate:** `COI-CMD-OPS-GUIDE-01` → **completed**  
**BLAST:** `docs/handoffs/2026-07-18-coi-cmd-ops-guide-01-BLAST.md`  
**Evidence base:** UX-POLISH LIVE tip `2ddc942` + `UX-DOGFOOD-PHONE.md`

## Shipped (flex-vcms)

1. `docs/study/coi-commander-ops-handbook.md` — 5 scenariuszy (cold-open, lead hot, Marketing, Delegat, no-laptop) + hops + STOP  
2. `docs/study/study-index.md` — sekcja **Ops System** + zachowany Vibe Coach pointer  
3. `docs/index.md` NAUKA — link „COI Commander — instrukcja obslugi”

## DoD

| Kryterium | Status |
|-----------|--------|
| Handbook 5 scenariuszy z evidence | PASS |
| study-index + docs/index links | PASS |
| Zero secrets / mint / Gate D unlock | PASS |
| Vibe Coach skill-map nietknięty (tylko pointer) | PASS |

## Ship evidence (2026-07-18 GO closeout)

| Repo | Tip / PR | Status |
|------|----------|--------|
| jadzia-core | `8e4f81a` | pushed + VPS `/opt/jadzia` pulled |
| flex-vcms | PR [#23](https://github.com/wozniaknorbert95-del/Flex-vcms/pull/23) → master `a6d5407` | merged |
| VCMS prod docs | dist upload + `pm2 reload vcms-core` | **LIVE** |

Prod verify (localhost on VPS):

- health `{"status":"OK"}`
- `GET /docs/study/coi-commander-ops-handbook` → **200** + „Cold-open dnia”
- Public: https://cmd.flexgrafik.nl/docs/study/coi-commander-ops-handbook (Basic Auth)

Note: full `Deploy-VPS.ps1` hung on first SSH after build; shipped via tarball `docs/.vitepress/dist` → `/var/www/vcms/current/.../dist` (same DoD for docs pages).

## PARK

Gate D · Mollie · mint/recover · OS merge · MBA regen

## NEXT

Human: walkthrough cold-open wg handbook (optional).  
Agent: idle / next non-MBA feature.

```text
HANDOFF_FILE: docs/handoffs/2026-07-18-coi-cmd-ops-guide-01-CLOSE.md
BACKLOG_ID: COI-CMD-OPS-GUIDE-01
STATE: completed LIVE — handbook on cmd.flexgrafik.nl/docs/study/
```
