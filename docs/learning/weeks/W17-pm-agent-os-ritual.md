# Week 17 — PM Agent OS ritual

**Status:** Agent wdrożenie DONE · Dowódca PASS pending (UI Basic Auth)  
**Date:** 2026-07-18  
**Gate:** COI-PM-01 (maintain)  
**Spine:** tydz. 17

## Cel

Jeden rytuał **AI Project Manager**: hop do Agent OS → jedna task HITL approve → DONE. Lekcja = `COI-PM-01` już PASS — **nie** merge OS do jadzia (ADR D0.6).

## Treść (mikro)

1. **Kontrakt (D0.20 §3):** orkiestracja kodu / HITL diffs; hop `os.flexgrafik.nl`; `agent_id=engineering`.  
2. **Powierzchnie:** UI Mission Control (Basic Auth — path Dowódcy); API `os-api.flexgrafik.nl` (health + approve).  
3. **Ritual:** open REVIEWING → `POST /tasks/{id}/approve` → status DONE. Dowód: `task-4f6a23d8` → DONE (2026-07-18).  
4. **No merge:** Commander deep-link only; OS i jadzia = osobne deploy units.  
5. **HITL always** na diffs — nie mylić z HOTL marketing/sales (W14).

## Wdrożenie (dowód)

| Artefakt | Link |
|----------|------|
| PM-01 CLOSE | [coi-pm-01-CLOSE](../../handoffs/2026-07-18-coi-pm-01-CLOSE.md) |
| PM-01 BLAST | [coi-pm-01-BLAST](../../handoffs/2026-07-18-coi-pm-01-BLAST.md) |
| Role contract | [D0.20 §3 AI PM](../../design/coi-commander/specs/D0.20-ai-role-contracts.md) |
| Process | [P-ENG-01](../../ops/PROCESS-CATALOG.md) LIVE |
| No-merge ADR | [D0.6-phone-hub-not-merge](../../design/coi-commander/adr/D0.6-phone-hub-not-merge.md) |
| Scorecard #5 | [SCORECARD](../../ops/SCORECARD-AI-OS-ZALICZENIE.md) AI Project Manager LIVE |

## Dowódca

- [ ] PASS — jedna HITL approve w Mission Control (phone/UI OK; Basic Auth)  
- [ ] FAIL — (powód)

## Następny tydzień

W18 — CS BLAST scope — osobny gate (maintain COI-CS-01).
