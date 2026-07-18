# Week 12 — Ops AI interim read

**Status:** Agent wdrożenie DONE · Dowódca PASS pending  
**Date:** 2026-07-18  
**Gate:** COI-OPS-AI-01 (maintain / interim read)  
**Spine:** tydz. 12

## Cel

**Interim read** kontraktu ≥60% ops AI: formuła v1.1, ostatni wynik 14d, kiedy robić re-window. Lekcja = rytuał odczytu już LIVE PASS — **nie** nowy deploy ani świeży SQL w tej sesji.

## Treść (mikro)

1. **Formuła:** `ops_ai_ratio = ai / (ai + human)`; target ≥ 0.60; CRITICAL HITL excluded.  
2. **v1.1 klasy:** AI = `brief_*` + `cs_followup` + leads created + widget sessions; Human = audit publish + leads closed.  
3. **Ostatni PASS:** **20/33 = 60.6%** @ tip `d97939a` (2026-07-18).  
4. **Re-window:** gdy spike human publish lub zmiana instrumentacji — świeży count tylko z GO + skrypt SoT; nie zgadywać %.

## Wdrożenie (dowód)

| Artefakt | Link |
|----------|------|
| OPS-AI scorecard | [OPS-AI-SCORECARD.md](../../ops/OPS-AI-SCORECARD.md) PASS/LIVE |
| OPS-AI-01 CLOSE | [coi-ops-ai-01-CLOSE](../../handoffs/2026-07-18-coi-ops-ai-01-CLOSE.md) |
| Scorecard #9 | [SCORECARD](../../ops/SCORECARD-AI-OS-ZALICZENIE.md) ≥60% LIVE |
| Todo gate | `COI-OPS-AI-01` completed |

## Dowódca

- [ ] PASS — przeczytane W12 + otwarte OPS-AI-SCORECARD (rozumie 60.6% vs baseline 45.8%)  
- [ ] FAIL — (powód)

## Następny tydzień

W13 — Q1 gate review — osobny gate.
