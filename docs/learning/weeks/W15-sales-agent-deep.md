# Week 15 — Sales agent contract deep

**Status:** Agent wdrożenie DONE · Dowódca PASS pending (phone optional)  
**Date:** 2026-07-18  
**Gate:** ROLE sales / REV-DEMAND maintain  
**Spine:** tydz. 15

## Cel

Głęboki kontrakt **AI Sprzedawca**: CTA SLA + disposition QA. Lekcja = D0.20 §1 + kolejka `sales_cta` już LIVE — nie nowe API, nie płatność (W09 = path dogfood; tu = jakość HITL).

## Treść (mikro)

1. **Kontrakt (D0.20):** Lead → oferta/CTA → Wizard (≥199, wizard-only); wyjścia: reply NL, lead row, `sales_cta` ticket.  
2. **CTA SLA:** kolejka `sales_cta` = ACTION; SLA **4h** (brief spawn score≥40); human Ack/Snooze/Close.  
3. **Disposition QA:** lead + ticket — Ack = wzięte; Snooze = świadome odłożenie; Close = zamknięte z powodem w praktyce (bez „ghost open”).  
4. **Score gate:** CTA / spawn gdy `max(AI, LeadScorer) ≥ 40` lub intent high — nie spam niskiego score.  
5. **Poza lekcją:** Gate D / Mollie; HOTL graduate sales (W14) — CRITICAL sales disposition zostaje HITL.

## Wdrożenie (dowód)

| Artefakt | Link |
|----------|------|
| Role contract | [D0.20 §1 AI Sprzedawca](../../design/coi-commander/specs/D0.20-ai-role-contracts.md) |
| Process | [P-SALES-01 / P-SALES-02](../../ops/PROCESS-CATALOG.md) LIVE |
| Brief → sales_cta | [rev-demand-04-CLOSE](../../handoffs/2026-07-18-rev-demand-04-CLOSE.md) |
| Path dogfood (W09) | [W09-sales-path-dogfood](./W09-sales-path-dogfood.md) |
| Scorecard #3 | [SCORECARD](../../ops/SCORECARD-AI-OS-ZALICZENIE.md) AI Sprzedawca LIVE |
| Dogfood playbook | [JADZIA-REVENUE-DOGFOOD](../../ops/JADZIA-REVENUE-DOGFOOD.md) §6–7 |

## Dowódca

- [ ] PASS — jedna dyspozycja `sales_cta` (Ack lub Close) z sensem SLA / QA (phone OK)  
- [ ] FAIL — (powód)

## Następny tydzień

W16 — Marketing agent depth — osobny gate.
