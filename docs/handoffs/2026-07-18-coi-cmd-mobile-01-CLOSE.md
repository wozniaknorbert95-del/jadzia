# Handoff — COI-CMD-MOBILE-01 phone-first Commander hub

**Date:** 2026-07-18  
**Repo:** jadzia-core  
**Status:** ready_for_deploy → LIVE after GO redeploy  
**Owner:** COI Commander mobile hub  
**Fundacja:** `docs/handoffs/2026-07-18-ssot-demand-CLOSE.md`

## DONE

| Item | Result |
|------|--------|
| ADR | `docs/design/coi-commander/adr/D0.6-phone-hub-not-merge.md` |
| Mobile shell | sticky bottom nav ≤600px; touch ≥44px; Więcej → Audyt/Ustawienia |
| System map | Home links + Settings read-only URLs |
| API | unchanged |
| Parks | untouched |
| REV-DEMAND-04 | still blocked until this LIVE (then gate returns) |

## DEPLOY

Redeploy `/opt/jadzia` master (static `commander-ui/` + docs). Restart `jadzia` for static refresh.

## Smoke

- [ ] `GET /commander/` 200
- [ ] Home shows system map
- [ ] ≤420px: bottom nav visible

## NEXT SESSION START

```text
STATE: SSoT clean; COI-CMD-MOBILE-01 LIVE; Demand 01-03 evidence PASS
NEXT: @blast REV-DEMAND-04 brief HITL → sales CTA tickets
ALT_ONLY_IF_HUB_BROKEN: fix mobile hub (1-1-1) before 04
STOP: Gate D; Mollie; park deletes; Agent OS merge
```
