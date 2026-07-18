# Week 18 — CS BLAST (scope locked)

**Status:** Agent wdrożenie DONE · Dowódca PASS pending  
**Date:** 2026-07-18  
**Gate:** COI-CS-01 (BLAST / scope)  
**Spine:** tydz. 18

## Cel

Zrozumieć **BLAST CS**: dlaczego CS był GAP, czym różni się od Sales, jaki thin slice zablokowano przed implementacją. Lekcja = dokument scope (`COI-CS-01`) — **nie** kod (to W19 / CS-02).

## Treść (mikro)

1. **Pre-sale ≠ post-sale:** `sales_cta` (W09/W15) ≠ CS follow-up po płatności.  
2. **Thin slice locked:** `source=cs_followup` + queue `cs_followup` (ACTION, SLA **48h**).  
3. **Trigger v1:** ręczny spawn (Commander / order_id) — **bez** auto-spam; auto-trigger later.  
4. **HITL reuse:** Ack / Snooze / Close (jak inne kolejki).  
5. **STOP w BLAST:** SSO, Agent OS merge, auto-email klienta bez GO, Mollie LIVE, Gate D, zewnętrzny helpdesk.

## Wdrożenie (dowód)

| Artefakt | Link |
|----------|------|
| Scope BLAST | [coi-cs-01-BLAST](../../handoffs/2026-07-18-coi-cs-01-BLAST.md) |
| Role contract | [D0.20 §4 AI CS](../../design/coi-commander/specs/D0.20-ai-role-contracts.md) |
| Process (po CS-02) | [P-CS-01](../../ops/PROCESS-CATALOG.md) COVERED |
| Implement (W19) | [coi-cs-02-CLOSE](../../handoffs/2026-07-18-coi-cs-02-CLOSE.md) — osobna lekcja |
| Scorecard #6 | [SCORECARD](../../ops/SCORECARD-AI-OS-ZALICZENIE.md) AI CS LIVE (po CS-02) |

## Dowódca

- [ ] PASS — przeczytane W18 + CS-01 BLAST; rozumie scope vs Sales CTA  
- [ ] FAIL — (powód)

## Następny tydzień

W19 — CS implement slice (API+UI HITL) — osobny gate.
