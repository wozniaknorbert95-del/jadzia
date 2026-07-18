# Week 14 — HITL vs HOTL policy

**Status:** Agent wdrożenie DONE · Dowódca PASS pending  
**Date:** 2026-07-18  
**Gate:** D0.11 apply (maintain)  
**Spine:** tydz. 14 · **Q2 start**

## Cel

Zrozumieć i stosować **HITL vs HOTL**: człowiek w pętli vs na pętli, progi graduacji D0.11, kiedy **nie** graduate. Lekcja = polityka już w spec + F3 runtime — nie nowy kod ani live graduate w tej sesji.

## Treść (mikro)

1. **HITL** — akcja czeka na approve/edit człowieka (queue / Home).  
2. **HOTL** — auto z notify; człowiek nadzoruje, wkracza przy spike override.  
3. **Progi D0.11** (per action-type): `approved_without_edit ≥ N` (default 20) **oraz** `override_rate < X%` (default 5%, 30d) **oraz** `confidence_avg ≥ threshold` → HOTL.  
4. **Revert** na override spike; badge UI: HITL / HOTL / auto.  
5. **Never graduate (Always HITL):** CRITICAL queue, public marketing publish, deploy, Gate D, payment. Safe auto (bez extra HITL): widget replies, lead create, brief/cs spawn, freshness — patrz OPS-AI safe list.

## Wdrożenie (dowód)

| Artefakt | Link |
|----------|------|
| Spec D0.11 | [D0.11-graduation.md](../../design/coi-commander/specs/D0.11-graduation.md) |
| UX brief CE-08 | [UX-BRIEF-COMMANDER](../../design/coi-commander/UX-BRIEF-COMMANDER.md) |
| F3 / v3 CLOSE | [coi-commander-v3-CLOSURE-PROOF](../../handoffs/2026-07-09-coi-commander-v3-CLOSURE-PROOF.md) |
| OPS safe list | [OPS-AI-SCORECARD](../../ops/OPS-AI-SCORECARD.md) (Automation safe list) |

## Dowódca

- [ ] PASS — przeczytane W14 + D0.11; wie które akcje nigdy nie graduate  
- [ ] FAIL — (powód)

## Następny tydzień

W15 — Sales agent contract deep — osobny gate.
