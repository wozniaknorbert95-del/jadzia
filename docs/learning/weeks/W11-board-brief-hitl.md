# Week 11 — Board brief HITL ritual

**Status:** Agent wdrożenie DONE · Dowódca PASS pending (phone optional)  
**Date:** 2026-07-18  
**Gate:** COI-STRATEGY-HITL-01 (maintain)  
**Spine:** tydz. 11

## Cel

Jeden cykl **weekly board brief HITL**: metrics → rekomendacje → draft tickets w Commander → human approve/act na Home. Lekcja = ścieżka już LIVE — **bez auto-execute** (SSH/publish/pay).

## Treść (mikro)

1. **Brief node** zbiera KPI / hygiene sygnały (GA4, revenue counts, FB hygiene).  
2. **Spawn HITL tickets** — `source=brief_hitl`, status `open`, dedup po tytule+source.  
3. **Home / queue** — Dowódca approve lub dismiss; AI nie wykonuje akcji krytycznych sam.  
4. **Ticket hygiene** — ops drafts tylko; sales_cta / marketing publish idą osobnymi torami HITL.

## Wdrożenie (dowód)

| Artefakt | Link |
|----------|------|
| Process card | [PROCESS-CATALOG P-BOARD-01](../../ops/PROCESS-CATALOG.md) LIVE |
| STRATEGY CLOSE | [coi-readiness-Aplus-CLOSE](../../handoffs/2026-07-18-coi-readiness-Aplus-CLOSE.md) |
| Scorecard #7 | [SCORECARD](../../ops/SCORECARD-AI-OS-ZALICZENIE.md) AI Asystent Zarządu LIVE |
| Todo gate | `COI-STRATEGY-HITL-01` completed (`brief_node` + tests) |

## Dowódca

- [ ] PASS — cold path: otwórz Home → widać / obsłuż jeden ticket `brief_hitl` (phone OK)  
- [ ] FAIL — (powód)

## Następny tydzień

W12 — Ops AI interim read — osobny gate.
