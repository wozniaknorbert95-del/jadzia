# Design: Jadzia Spine Closure → 85% + Operator School

**Date:** 2026-07-08  
**Status:** ACTIVE  
**Owner:** Norbert Wozniak (Dowódca)  
**Repo:** jadzia-core

---

## North star

Close the **operational COI spine** at ~85% readiness (definition: 7 LIVE capabilities in `services/src/content/jadzia-coi.ts`), sync documentation truth, prove prod, then train the Commander on daily operation (Telegram + COI API).

## Definition of 85%

| # | Capability | Contract | In spine |
|---|------------|----------|----------|
| 1 | Order intelligence | INT-002 | YES |
| 2 | Lead unification | INT-004 | YES |
| 3 | GA4 snapshot | INT-009 | YES |
| 4 | Content calendar | INT-010 | YES |
| 5 | Sales chat widget | INT-001 | YES |
| 6 | WordPress SSH agent | Telegram/worker | YES |
| 7 | Worker queue + HITL | JWT worker API | YES |
| 8 | Weekly brief | `brief_node` + worker hook | YES (proof required) |
| — | Procurement Brain | Phase C | NO |
| — | Agent OS auto-spawn | INT-006 | NO |
| — | Design Agent INSPIRE v2 | Separate product track | NO (documented separately) |

## Out of scope

- S1-01 secret rotation (deferred parallel gate — Dowódca only)
- Procurement Phase C, B3.1 FB sense, TikTok C1-01
- Design Agent feature work (INSPIRE deploy closure only)
- Building a web UI dashboard (JSON API only today)

## Phases

### Fase 1 — TRUTH SYNC

Sync `brain.md`, `todo.json`, flexgrafik-meta module spec + charter, INSPIRE handoff, F1 handoff.

**DoD:** No doc says orders/leads PLANNED; `readiness_overall` ~85% spine; 12 SC85 tasks in todo.

### Fase 2 — SPINE PROOF

Fill `docs/ops/JADZIA-SPINE-PROOF-MATRIX.md` with C1–C7 PASS/FAIL on prod.

**DoD:** 7/7 PASS or explicit waiver; F2 handoff committed.

### Fase 3 — S1-01 (DEFERRED)

Checklist: `docs/handoffs/2026-07-03-s1-01-secret-rotation-checklist.md`

### Fase 4 — OPERATOR SCHOOL

`docs/ops/JADZIA-OPERATOR-PLAYBOOK.md` + Commander exercises E1–E3.

**DoD:** Playbook committed; E1+E2 confirmed; program closed in todo.

## Global program DoD

- [ ] 7/7 spine PASS in proof matrix
- [ ] `brain.md` overall ~85%
- [ ] Operator playbook exists
- [ ] Commander completed E1+E2
- [ ] INSPIRE handoff in repo
- [ ] S1-01 remains open (documented in F4 handoff)

## References

- Proof matrix: `docs/ops/JADZIA-SPINE-PROOF-MATRIX.md`
- Playbook: `docs/ops/JADZIA-OPERATOR-PLAYBOOK.md`
- Portfolio capabilities: `services/src/content/jadzia-coi.ts`
- Deploy closure: `docs/handoffs/2026-07-05-deploy-closure-complete.md`
