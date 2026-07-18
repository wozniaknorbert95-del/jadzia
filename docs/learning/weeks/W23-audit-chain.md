# Week 23 — Audit chain ritual

**Status:** Agent wdrożenie DONE · Dowódca PASS pending  
**Date:** 2026-07-18  
**Gate:** D0.10 apply (maintain)  
**Spine:** tydz. 23

## Cel

Tygodniowy rytuał **weryfikacji audit hash-chain**: rozliczalność mutacji Commander. Lekcja = D0.10 LIVE (v3) — nie kasuj logów; nie świeży VPS probe bez GO.

## Treść (mikro)

1. **Storage:** `commander_audit_log` INSERT-only — brak UPDATE/DELETE na app path.  
2. **Hash-chain:** `row_hash = SHA256(prev_hash + canonical_json)` — przerwa łańcucha = alarm.  
3. **Pola:** actor, role, action, source, target, before/after, reason, risk_tier, session, prev/row hash.  
4. **Retention:** 24 miesiące; export przed purge (GDPR).  
5. **Readers:** Dowódca + Delegat read; Viewer **no**. UI: `/audit-log` (role-gated).  
6. **Ritual:** raz/tydzień otwórz audit-log → spot-check ostatnie publish/disposition → łańcuch spójny.

## Wdrożenie (dowód)

| Artefakt | Link |
|----------|------|
| Spec D0.10 | [D0.10-audit-log.md](../../design/coi-commander/specs/D0.10-audit-log.md) |
| v3 CLOSURE | [coi-commander-v3-CLOSURE-PROOF](../../handoffs/2026-07-09-coi-commander-v3-CLOSURE-PROOF.md) |
| Authz (W22) | [W22-authz-scopes](./W22-authz-scopes.md) |

## Dowódca

- [ ] PASS — otwarte audit-log (lub przeczytane D0.10 + rozumie ritual)  
- [ ] FAIL — (powód)

## Następny tydzień

W24 — Cross-role handoff map — osobny gate.
