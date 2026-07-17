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

## Faza 1 — COI-CMD-QUEUE-CLEAN — DONE (prod 2026-07-17)

| Step | Result |
|------|--------|
| VPS sync | `reset --hard origin/master` @ `33e58b9` (local dirty tree stashed as `vps-pre-queue-clean-20260717`) |
| DB backup | `data/jadzia.db.bak.*-queue-clean` |
| Dry-run | 3 matches (`deploy02-*`, `int004-e2e-*`) |
| Apply | **deleted=3** |
| Remaining | `jan@bouw.com`, `bob@gamil.com` only |
| `jadzia` | active |

**Gate:** `COI-CMD-QUEUE-CLEAN` → **completed**

---

## Faza 2 — NEXT session (expansion)

1. **Human:** Marketing smoke 2 min — https://api.zzpackage.flexgrafik.nl/commander/ → fb-health, filtr Opublikowane (QR)
2. **Agent COI:** `/blast` → `COI-CONTENT-INTAKE-M2` (video/Reels)
3. **Agent DA (osobna sesja):** review/merge `feat/da-insire-enterprise`; resolve `stash@{0}` inspire safety vs enterprise `engine.py`

Optional: FB token rotation (`docs/ops/FB-TOKEN-ROTATION.md`)

---

## Refs

- Prior: `docs/handoffs/2026-07-09-coi-marketing-session-HANDOFF.md`
- FB ops: `docs/ops/FB-TOKEN-ROTATION.md`
