# Week 19 — CS implement slice

**Status:** Agent wdrożenie DONE · Dowódca PASS pending (phone optional)  
**Date:** 2026-07-18  
**Gate:** COI-CS-02 (maintain)  
**Spine:** tydz. 19

## Cel

Zaliczyć **implementację CS** (API + Home UI HITL): spawn `cs_followup` → disposition. Lekcja = `COI-CS-02` już LIVE — nie nowy kod; auto-trigger paid-order = poza scope.

## Treść (mikro)

1. **Spawn:** `POST /api/v1/commander/cs/followup` → ticket `source=cs_followup` w kolejce ACTION.  
2. **HITL UI:** Home form + PL **Potwierdź / Odłóż / Zamknij** (`disposition` acked|snoozed|closed).  
3. **SLA:** &lt;48h na human act (P-CS-01); W18 locked scope.  
4. **Dogfood:** tip `0a54bc7` — spawn `#12`/`#13` → toast `Ticket 13 → acked`.  
5. **Residual:** auto-trigger z paid order = later; nie auto-email klienta bez GO.

## Wdrożenie (dowód)

| Artefakt | Link |
|----------|------|
| CS-02 CLOSE | [coi-cs-02-CLOSE](../../handoffs/2026-07-18-coi-cs-02-CLOSE.md) |
| Scope (W18) | [W18-cs-blast](./W18-cs-blast.md) |
| Process | [P-CS-01](../../ops/PROCESS-CATALOG.md) LIVE |
| Role | [D0.20 §4 AI CS](../../design/coi-commander/specs/D0.20-ai-role-contracts.md) |
| Scorecard #6 | [SCORECARD](../../ops/SCORECARD-AI-OS-ZALICZENIE.md) AI CS LIVE |

## Dowódca

- [ ] PASS — jedna sesja: spawn CS → Potwierdź/Ack (phone OK)  
- [ ] FAIL — (powód)

## Następny tydzień

W20 — Board assistant depth — osobny gate.
