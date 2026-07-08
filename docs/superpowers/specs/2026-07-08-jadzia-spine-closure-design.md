# Design: Jadzia COI Spine Closure (58% → 85%)

**Date:** 2026-07-08  
**Owner:** Agent (senior closure)  
**Status:** APPROVED — executing  
**Scope:** Truth sync + spine proof + operator playbook. **Out:** Design Agent feature work, S1-01 execution (human), Procurement Phase C.

---

## Problem

Three truth layers diverged:

- Desktop notes / meta docs (June) → orders PLANNED, ~35–40%
- `jadzia-core` code + prod (July) → Phase A+B LIVE, smoke 8/8
- Commander mental model → expects panel + chat; AS-IS is Telegram + JSON API

**Goal:** One operational spine at **~85%** (7 LIVE capabilities per `services/src/content/jadzia-coi.ts`), then operator training.

## Definition of 85%

| Capability | Contract | In 85%? |
|------------|----------|---------|
| Order intelligence | INT-002 | YES |
| Lead unification | INT-004 | YES |
| GA4 snapshot | INT-009 | YES |
| Content calendar | INT-010 | YES |
| Sales chat widget | INT-001 | YES |
| WP SSH agent | Telegram/worker | YES |
| Worker queue + HITL | JWT worker API | YES |
| Weekly brief | S3-02 worker hook | YES (verify) |
| Procurement Brain | Phase C | NO |
| Agent OS auto-spawn | INT-006 | NO |
| Design Agent INSPIRE | Separate product | CLOSED separately |

## Execution order (senior — no Commander gates between phases)

1. **Truth sync** — `brain.md`, `todo.json`, `flexgrafik-meta/module-jadzia-core.md`, handoffs index
2. **Spine proof** — VPS prod-smoke + proof matrix with evidence links
3. **Operator playbook** — Telegram + API map + 3 exercise scenarios
4. **S1-01** — parallel human gate (checklist unchanged; not blocking spine label)

## Deliverables

| File | Purpose |
|------|---------|
| `docs/ops/JADZIA-SPINE-PROOF-MATRIX.md` | 7/7 capability PASS matrix |
| `docs/ops/JADZIA-OPERATOR-PLAYBOOK.md` | Commander daily ops guide |
| `docs/handoffs/2026-07-08-da-inspire-deploy-FINAL.md` | INSPIRE closure record |
| `docs/handoffs/2026-07-08-jadzia-spine-closure-complete.md` | Session handoff |

## Exit criteria

- [x] `brain.md` overall readiness ~85% operational spine
- [x] `todo.json` active_gate → `operator-school` (S1-01 parallel)
- [x] VPS prod-smoke 8/8 documented
- [x] Operator playbook exists
- [ ] Commander completes 3 playbook exercises (human)
- [ ] S1-01 secret rotation (human)

## Rollback

Docs-only session — revert commits. No prod deploy in this session.
