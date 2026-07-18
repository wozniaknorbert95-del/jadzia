# Week 09 — Sales path dogfood

**Status:** Agent wdrożenie DONE · Dowódca PASS pending (phone optional)  
**Date:** 2026-07-18  
**Gate:** REV-DEMAND F0–F7 (maintain)  
**Spine:** tydz. 9

## Cel

Ścieżka AI Sprzedawca: widget → lead → Commander disposition → Wizard CTA — **bez płatności**. Lekcja = łańcuch już LIVE, nie nowe API.

## Treść (mikro)

1. **Widget** odpowiada NL + scoring; CTA gdy `max(AI, LeadScorer) ≥ 40` lub intent high.  
2. **Lead** durable w SQLite (email+consent / inspire bridge).  
3. **Commander** hot_lead + `sales_cta` z brief HITL.  
4. **Wizard deeplink** = jedyna droga zakupu (Wizard-only); Gate D / Mollie poza lekcją.

## Wdrożenie (dowód)

| Artefakt | Link |
|----------|------|
| Program CLOSE | [rev-demand-PROGRAM-CLOSE](../../handoffs/2026-07-18-rev-demand-PROGRAM-CLOSE.md) |
| F0–F4 | [rev-demand-01-CLOSE](../../handoffs/2026-07-18-rev-demand-01-CLOSE.md) |
| CTA score fix | [rev-demand-02a-CLOSE](../../handoffs/2026-07-18-rev-demand-02a-CLOSE.md) |
| Session durability | [rev-demand-02-CLOSE](../../handoffs/2026-07-18-rev-demand-02-CLOSE.md) |
| INSPIRE bridge | [rev-demand-03-CLOSE](../../handoffs/2026-07-18-rev-demand-03-CLOSE.md) |
| Brief sales_cta | [rev-demand-04-CLOSE](../../handoffs/2026-07-18-rev-demand-04-CLOSE.md) |
| Scorecard #3 | [SCORECARD](../../ops/SCORECARD-AI-OS-ZALICZENIE.md) LIVE |

## Dowódca

- [ ] PASS — cold path: jedna sesja widget → lead widać w Commander (phone OK)  
- [ ] FAIL — (powód)

## Następny tydzień

W10 — Marketing HITL ritual — osobny gate.
