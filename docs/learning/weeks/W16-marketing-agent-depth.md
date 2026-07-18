# Week 16 — Marketing agent depth

**Status:** Agent wdrożenie DONE · Dowódca PASS pending  
**Date:** 2026-07-18  
**Gate:** ROLE mkt / D0.8 apply (maintain)  
**Spine:** tydz. 16

## Cel

Głęboki kontrakt **AI Marketing**: **undo60** + **risk matrix drill**. Lekcja = D0.20 §2 + D0.8 + CE-05 już w Commander — nie live FB post (W10 = cykl HITL; tu = odwracalność i tier ryzyka).

## Treść (mikro)

1. **Kontrakt (D0.20):** Draft → approve → publish / undo; hop Marketing; `agent_id=marketing`.  
2. **Risk tier (D0.8):** FB approve = **sensitive** (1× HITL); bulk >5 / WP SSH = **high-impact** (dual-confirm) — nie mylić.  
3. **Undo semantics (N5/CE-05):**  
   - **public_publish** → unpublish/delete + audit + notify (60s nie cofa „zobaczenia” audience).  
   - **internal_state** → 60s soft undo.  
4. **SLA queue:** `fb_post_pending` ACTION 12h amber / 24h red; `scheduled_publish_due` ACTION 1h.  
5. **Always HITL:** public marketing publish — nie graduate do HOTL (W14). Failure path: `publish_failed` + TG (PUBLISH-B).

## Wdrożenie (dowód)

| Artefakt | Link |
|----------|------|
| Role contract | [D0.20 §2 AI Marketing](../../design/coi-commander/specs/D0.20-ai-role-contracts.md) |
| Risk matrix | [D0.8-risk-matrix-sla.md](../../design/coi-commander/specs/D0.8-risk-matrix-sla.md) |
| Process | [P-MKT-01](../../ops/PROCESS-CATALOG.md) LIVE |
| HITL path (W10) | [W10-marketing-hitl](./W10-marketing-hitl.md) |
| Undo/unpublish | [coi-commander-v3-CLOSURE-PROOF](../../handoffs/2026-07-09-coi-commander-v3-CLOSURE-PROOF.md) |
| Publish-B | [coi-marketing-publish-B-PROOF](../../handoffs/2026-07-09-coi-marketing-publish-B-PROOF.md) |
| Scorecard #4 | [SCORECARD](../../ops/SCORECARD-AI-OS-ZALICZENIE.md) AI Marketing LIVE |

## Dowódca

- [ ] PASS — przeczytane W16 + D0.8; potrafi rozróżnić public unpublish vs internal 60s  
- [ ] FAIL — (powód)

## Następny tydzień

W17 — PM Agent OS ritual — osobny gate (maintain COI-PM-01).
