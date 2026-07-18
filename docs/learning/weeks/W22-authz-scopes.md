# Week 22 — Authz scopes review

**Status:** Agent wdrożenie DONE · Dowódca PASS pending  
**Date:** 2026-07-18  
**Gate:** D0.13 apply (maintain)  
**Spine:** tydz. 22

## Cel

Przegląd **multi-role authz**: JWT `role` + scopes, mapa Settings, 403 vs UI hide. Lekcja = D0.13 LIVE — nie commituj tokenów.

## Treść (mikro)

1. **Roles:** `dowodca` | `delegat` | `viewer` (default `dowodca` jeśli omitted).  
2. **Scopes:** Dowódca `*`; Delegat = marketing+queue+leads+read; Viewer = `*:read` + `commander:read`.  
3. **Resolve:** `commander_roles` (Settings) → `resolve_role()` przed claim JWT.  
4. **Security:** UI hide ≠ security; backend **403** na violation.  
5. **Block escalate-through-UI:** Delegat nie nadaje roli Dowódca (`settings:roles`).  
6. **Dogfood (human):** `scripts/jwt_token.py --role delegat|viewer` — lokalnie; nie wrzucaj tokenów do git.

## Wdrożenie (dowód)

| Artefakt | Link |
|----------|------|
| Spec D0.13 | [D0.13-authz.md](../../design/coi-commander/specs/D0.13-authz.md) |
| Escalatacja (W21) | [W21-delegat-escalation](./W21-delegat-escalation.md) |
| UX CE-09 | [UX-BRIEF-COMMANDER](../../design/coi-commander/UX-BRIEF-COMMANDER.md) |

## Dowódca

- [ ] PASS — przeczytane W22 + D0.13; wie że 403 jest SoT bezpieczeństwa  
- [ ] FAIL — (powód)

## Następny tydzień

W23 — Audit chain ritual — osobny gate.
