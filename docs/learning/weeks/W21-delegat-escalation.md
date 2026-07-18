# Week 21 — Delegat escalation drill

**Status:** Agent wdrożenie DONE · Dowódca PASS pending (opcjonalny re-smoke)  
**Date:** 2026-07-18  
**Gate:** D0.9 + COI-CMD-SMTP-01 (maintain)  
**Spine:** tydz. 21

## Cel

Drill **eskalacji do Delegata**: timeline SLA amber/red → TG → email gdy Dowódca inactive. Lekcja = D0.9 + SMTP-01 CLOSED — nie nowe sekrety; świeży smoke tylko z GO human.

## Treść (mikro)

1. **Timeline (D0.9):** pending &gt;12h amber → &gt;24h red + push Dowódca → red **oraz** Dowódca inactive ≥24h → + email Delegat.  
2. **Kanały:** TG zawsze przy red; email tylko gdy `SMTP_HOST` + `delegat_email` + inactive.  
3. **Bez SMTP:** log `email skipped` — bez crashu; TG nadal działa.  
4. **Wymaganie prod:** min. 1 Delegat w Settings; bez Delegata → warning + fallback.  
5. **Authz:** Delegat nie awansuje siebie do Dowódcy (`settings:roles` — D0.13).  
6. **Evidence:** SMTP smoke PASS + inbox OK (2026-07-17 CLOSE) — re-smoke = human GO.

## Wdrożenie (dowód)

| Artefakt | Link |
|----------|------|
| Spec D0.9 | [D0.9-approval-escalation.md](../../design/coi-commander/specs/D0.9-approval-escalation.md) |
| SMTP CLOSE | [coi-cmd-smtp-01-CLOSE](../../handoffs/2026-07-17-coi-cmd-smtp-01-CLOSE.md) |
| Playbook | [SMTP-DELEGAT-ESCALATION](../../ops/SMTP-DELEGAT-ESCALATION.md) |
| Authz roles | [D0.13-authz](../../design/coi-commander/specs/D0.13-authz.md) |

## Dowódca

- [ ] PASS — przeczytane W21 + D0.9; wie kiedy idzie email vs tylko TG  
- [ ] FAIL — (powód)

## Następny tydzień

W22 — Authz scopes review — osobny gate.
