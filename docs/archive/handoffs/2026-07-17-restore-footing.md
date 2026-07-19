# Handoff — Restore footing 2026-07-17

**Branch:** `master` @ `4da9212` (+ verification polish)  
**Goal:** truth → hygiene → `COI-CMD-QUEUE-CLEAN` → expansion-ready  
**Status:** **COMPLETE + VERIFIED** 2026-07-17

---

## Definition of Done (Faza 0)

- [x] `origin/master` synced (`4da9212`)
- [x] Working tree on `master`, clean
- [x] `todo.json` / `brain.md` / `AGENTS.md` aligned with prod Marketing + QUEUE-CLEAN done
- [x] This handoff written

## Definition of Done (Faza 1)

- [x] Script `deployment/cleanup-e2e-hot-leads.py` + unit test
- [x] VPS DB backup + dry-run + apply
- [x] E2E leads gone; real leads kept
- [x] PROOF: `docs/handoffs/2026-07-17-coi-cmd-queue-clean-PROOF.md`

---

## Faza 0 — DONE

| Step | Result |
|------|--------|
| Push `origin/master` | `71bdf2e` → `33e58b9` → `4da9212` |
| Checkout | **`master`** (left `feat/da-insire-enterprise`) |
| `todo.json` | M2 task added; MARKETING-B note fixed; gate now `COI-CONTENT-INTAKE-M2` |
| `brain.md` | updated 2026-07-17 — Commander + Marketing LIVE |
| `AGENTS.md` | points to restore handoff + next gate M2 |

### Branch / stash policy (park)

| Item | Policy |
|------|--------|
| `feat/da-insire-enterprise` | **PARK** — +14 commits vs master; merge only in dedicated DA session |
| `feat/design-agent-v31` | PARK — ahead 1 local; do not mix with COI |
| `feat/design-agent-inspire-v2` | Historical; behind master |
| `feat/chatbot-widget-fix`, `claude/review-…` | Tech-debt; do not delete this session |
| Local `stash@{0}` | `WIP inspire engine safety retry` — **stash review pending** before DA merge |
| VPS `stash@{0}` | `vps-pre-queue-clean-20260717` — keep until Dowódca confirms no needed local diffs; do not auto-drop |

**Rule:** COI ops only on `master`. Never mix with INSPIRE branch.

---

## Faza 1 — COI-CMD-QUEUE-CLEAN — DONE (prod)

| Step | Result |
|------|--------|
| VPS sync | `reset --hard origin/master`; dirty tree → stash `vps-pre-queue-clean-20260717` |
| DB backup | `data/jadzia.db.bak.20260717-064605-queue-clean` |
| Apply | **deleted=3** (`deploy02-*`, `int004-e2e-*`) |
| Remaining | `jan@bouw.com`, `bob@gamil.com` |
| Re-verify dry-run | `match_count: 0` |
| `jadzia` / `/commander/` | active / 200 |

**Gate:** `COI-CMD-QUEUE-CLEAN` → **completed**

---

## Verification stamp (2026-07-17 post-plan)

| Check | Result |
|-------|--------|
| Local `master` == `origin/master` | `4da9212` |
| VPS HEAD | `4da9212` |
| E2E dry-run empty | YES |
| Unit tests cleanup + queue | 4 passed |
| Stale gate refs in brain/AGENTS | fixed (next = M2) |

---

## Faza 2 — NEXT session (expansion)

1. **Human:** Marketing smoke 2 min — https://api.zzpackage.flexgrafik.nl/commander/ → fb-health, filtr Opublikowane (QR)
2. **Agent COI:** `/blast` → `COI-CONTENT-INTAKE-M2` (video/Reels)
3. **Agent DA (osobna sesja):** review/merge `feat/da-insire-enterprise`; resolve local inspire stash vs enterprise `engine.py`

Optional: FB token rotation (`docs/ops/FB-TOKEN-ROTATION.md`)

---

## Refs

- PROOF: `docs/handoffs/2026-07-17-coi-cmd-queue-clean-PROOF.md`
- Prior: `docs/handoffs/2026-07-09-coi-marketing-session-HANDOFF.md`
- FB ops: `docs/ops/FB-TOKEN-ROTATION.md`
