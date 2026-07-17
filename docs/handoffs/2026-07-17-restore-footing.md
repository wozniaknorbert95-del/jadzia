# Handoff — Restore footing 2026-07-17

**Branch:** `master` @ push `71bdf2e` + this docs/cleanup commit  
**Goal:** truth → hygiene → `COI-CMD-QUEUE-CLEAN` → expansion-ready

---

## Faza 0 — DONE

| Step | Result |
|------|--------|
| Push `origin/master` | `71bdf2e` synced (was ahead 1) |
| Checkout | **`master`** (left `feat/da-insire-enterprise`) |
| `todo.json` | `active_gate=COI-CMD-QUEUE-CLEAN`; M2 task added; MARKETING-B note fixed |
| `brain.md` | updated 2026-07-17 — Commander + Marketing LIVE |
| `AGENTS.md` | active plan → this handoff / todo gate |

### Branch / stash policy (park)

| Item | Policy |
|------|--------|
| `feat/da-insire-enterprise` | **PARK** — +14 commits vs master; merge only in dedicated DA session |
| `feat/design-agent-v31` | PARK — ahead 1 local; do not mix with COI |
| `feat/design-agent-inspire-v2` | Historical; behind master |
| `feat/chatbot-widget-fix`, `claude/review-…` | Tech-debt; do not delete this session |
| `stash@{0}` | `WIP inspire engine safety retry` — **stash review pending** before any DA merge (compare to enterprise `engine.py`) |

**Rule:** COI ops only on `master`. Never commit QUEUE-CLEAN on INSPIRE branch.

---

## Faza 1 — COI-CMD-QUEUE-CLEAN

**Prod leads (2026-07-17 inspect):**

| id | email | Keep? |
|----|-------|-------|
| 1 | `deploy02-int004-…@flexgrafik.nl` | DELETE (E2E) |
| 2 | `deploy02-php-…@flexgrafik.nl` | DELETE (E2E) |
| 3 | `int004-e2e-…@flexgrafik.nl` | DELETE (E2E) |
| 4 | `jan@bouw.com` | KEEP |
| 5 | `bob@gamil.com` | KEEP |

**Script:** `deployment/cleanup-e2e-hot-leads.py`  
**Match:** email `deploy02-%` OR `int004-e2e-%`

---

## Faza 2 — NEXT session (not this commit's code)

1. Human: Marketing smoke (fb-health, QR published)
2. Agent: `/blast` → `COI-CONTENT-INTAKE-M2` **or** separate INSPIRE merge review
3. Optional: FB token rotation (`docs/ops/FB-TOKEN-ROTATION.md`)

---

## Refs

- Prior: `docs/handoffs/2026-07-09-coi-marketing-session-HANDOFF.md`
- FB ops: `docs/ops/FB-TOKEN-ROTATION.md`
