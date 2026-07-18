# Week 24 — Cross-role handoff map

**Status:** Agent wdrożenie DONE · Dowódca PASS pending  
**Date:** 2026-07-18  
**Gate:** PROC link (maintain)  
**Spine:** tydz. 24

## Cel

Mapa **przekazań między 5 rolami AI** — kto komu oddaje piłkę (process cards). Lekcja = PROCESS-CATALOG LIVE — nie nowe API.

## Treść (mikro)

| From → To | Handoff | Process |
|-----------|---------|---------|
| Board → Sales | brief spawn `sales_cta` | P-BOARD-01 → P-SALES-02 |
| Sales → (Wizard) | CTA deeplink; disposition | P-SALES-01 |
| Board/ops → Marketing | nie auto-publish; osobny HITL | P-MKT-01 |
| Sales paid → CS | post-sale (manual spawn v1) | P-CS-01 |
| Any → PM/OS | hop engineering HITL | P-ENG-01 |
| Critical SLA → Delegat | TG/SMTP escalate | D0.9 / W21 |

**Zasady:** nie mieszać torów w jednym tickecie; always-HITL (publish/pay/Gate D) nie przechodzi „bokiem” przez brief.

## Wdrożenie (dowód)

| Artefakt | Link |
|----------|------|
| PROCESS-CATALOG | [PROCESS-CATALOG.md](../../ops/PROCESS-CATALOG.md) |
| Role contracts | [D0.20](../../design/coi-commander/specs/D0.20-ai-role-contracts.md) |
| Scorecard 5 ról | [SCORECARD](../../ops/SCORECARD-AI-OS-ZALICZENIE.md) |

## Dowódca

- [ ] PASS — przeczytane W24; potrafi wskazać handoff Board→Sales i Sales→CS  
- [ ] FAIL — (powód)

## Następny tydzień

W25 — Q2 ops AI push — osobny gate.
