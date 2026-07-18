# Week 20 — Board assistant depth

**Status:** Agent wdrożenie DONE · Dowódca PASS pending  
**Date:** 2026-07-18  
**Gate:** ROLE board / STRATEGY-HITL maintain  
**Spine:** tydz. 20

## Cel

Głęboki kontrakt **AI Asystent Zarządu**: **jakość briefu** + **higiena ticketów**. Lekcja = D0.20 §5 + STRATEGY LIVE — W11 = rytuał cyklu; tu = kryteria jakości i porządek kolejki.

## Treść (mikro)

1. **Kontrakt:** Brief → Home priorities / HITL; wyjścia `brief_hitl` (+ `sales_cta` spawn na innym torze).  
2. **Brief quality bar:**  
   - sygnały z metryk (GA4 / revenue / FB hygiene), nie ogólniki;  
   - rekomendacja → **jeden** actionable ticket (nie wall of text);  
   - severity/SLA zgodne z D0.8 (INFO/ACTION; nie udawać CRITICAL bez powodu).  
3. **Ticket hygiene:**  
   - dedup po tytule+source (otwarte duplikaty = FAIL higieny);  
   - Ack / Snooze / Close — zero „ghost open”;  
   - ops drafts only; publish/pay/SSH **nie** z brief auto-execute.  
4. **Separation:** `sales_cta` / `cs_followup` / marketing = osobne tory HITL (nie mieszać w jednym tickecie).  
5. **Never auto-execute** CRITICAL paths z briefu (W14 always-HITL).

## Wdrożenie (dowód)

| Artefakt | Link |
|----------|------|
| Role | [D0.20 §5 AI Asystent Zarządu](../../design/coi-commander/specs/D0.20-ai-role-contracts.md) |
| Ritual (W11) | [W11-board-brief-hitl](./W11-board-brief-hitl.md) |
| Process | [P-BOARD-01](../../ops/PROCESS-CATALOG.md) LIVE |
| STRATEGY CLOSE | [coi-readiness-Aplus-CLOSE](../../handoffs/2026-07-18-coi-readiness-Aplus-CLOSE.md) |
| Risk/SLA | [D0.8-risk-matrix-sla](../../design/coi-commander/specs/D0.8-risk-matrix-sla.md) |
| Scorecard #7 | [SCORECARD](../../ops/SCORECARD-AI-OS-ZALICZENIE.md) LIVE |

## Dowódca

- [ ] PASS — przegląd Home: jeden `brief_hitl` oceniony (quality + hygiene OK lub poprawiony)  
- [ ] FAIL — (powód)

## Następny tydzień

W21 — Delegat escalation drill — osobny gate.
