# Week 25 — Q2 ops AI push

**Status:** Agent wdrożenie DONE · Dowódca PASS pending  
**Date:** 2026-07-18  
**Gate:** OPS-AI push / maintain  
**Spine:** tydz. 25

## Cel

Push automacji w ramach **safe list** (bez CRITICAL HITL). Lekcja = OPS-AI-01 już **60.6% PASS** — nie forge nowego %; nie VPS count bez GO.

## Treść (mikro)

1. **Target Q2:** utrzymać ≥60% ops AI (v1.1); nie cofać instrumentacji widget `created_at`.  
2. **Safe auto (bez extra HITL):** widget replies, lead create, brief INFO/ACTION spawn, `cs_followup` spawn, freshness polls.  
3. **Always HITL:** CRITICAL queue, public marketing publish, deploy, Gate D, payment.  
4. **Push ≠ spam:** więcej AI ops tylko z istniejącego kontraktu — nie auto-email / nie auto-publish.  
5. **Re-window:** tylko przy spike human publish lub zmianie kontraktu + GO.

## Wdrożenie (dowód)

| Artefakt | Link |
|----------|------|
| OPS-AI scorecard | [OPS-AI-SCORECARD](../../ops/OPS-AI-SCORECARD.md) 60.6% PASS |
| Interim (W12) | [W12-ops-ai-interim](./W12-ops-ai-interim.md) |
| OPS-AI-01 CLOSE | [coi-ops-ai-01-CLOSE](../../handoffs/2026-07-18-coi-ops-ai-01-CLOSE.md) |
| Scorecard #9 | [SCORECARD](../../ops/SCORECARD-AI-OS-ZALICZENIE.md) |

## Dowódca

- [ ] PASS — przeczytane W25 + safe list vs always-HITL  
- [ ] FAIL — (powód)

## Następny tydzień

W26 — Q2 gate review — osobny gate.
