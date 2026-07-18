# Week 08 — Knowledge hygiene

**Status:** Agent wdrożenie DONE · Dowódca PASS pending  
**Date:** 2026-07-18  
**Gate:** COI-KNOW-00 / COI-KNOW-01 (+ COI-PROC-02 process pointer)  
**Spine:** [AI-MBA-FLEXGRAFIK-SPINE.md](../AI-MBA-FLEXGRAFIK-SPINE.md) tydz. 8

## Cel

Jedna hierarchy SoT wiedzy — zero sprzecznych kanonów między jadzia / meta / VCMS. Lekcja = wdrożone pointery, nie kopia katalogów.

## Treść (mikro)

1. **SoT żyje w jadzia-core** — `docs/ops/KNOWLEDGE-SYSTEM-INDEX.md` + scorecard + PROCESS-CATALOG.  
2. **Mirror = pointer** — meta i VCMS linkują, nie duplikują tabel statusów.  
3. **Anty-drift** — active gate tylko z `todo.json`; handoff nie nadpisuje konstytucji.  
4. **Procesy** — karty L1 w PROCESS-CATALOG; VCMS `ai-os-processes` tylko jako hub.

## Wdrożenie (dowód)

| Artefakt | Link |
|----------|------|
| Knowledge index | [KNOWLEDGE-SYSTEM-INDEX.md](../../ops/KNOWLEDGE-SYSTEM-INDEX.md) |
| KNOW-01 CLOSE | [2026-07-18-coi-know-01-CLOSE.md](../../handoffs/2026-07-18-coi-know-01-CLOSE.md) |
| PROCESS-CATALOG LIVE | [PROCESS-CATALOG.md](../../ops/PROCESS-CATALOG.md) |
| PROC-02 CLOSE | [2026-07-18-coi-proc-02-CLOSE.md](../../handoffs/2026-07-18-coi-proc-02-CLOSE.md) |
| Scorecard #2+#8 | [SCORECARD-AI-OS-ZALICZENIE.md](../../ops/SCORECARD-AI-OS-ZALICZENIE.md) |
| VCMS processes (prod) | `/docs/ecosystem/ai-os-processes` (200 po dist) |

## Dowódca

- [ ] PASS — przeczytane W08 + otwarte KNOW index + VCMS processes link  
- [ ] FAIL — (powód)

## Następny tydzień (nie w tym gate)

W09 — Sales path dogfood (REV maintain) — osobny `/blast`.
