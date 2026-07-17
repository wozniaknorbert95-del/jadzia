# BLAST — DA-INSIRE-ENTERPRISE-MERGE (queued)

**Date:** 2026-07-17  
**Status:** QUEUED — start after FB token rotation + optional M2 Graph E2E retry  
**Branch:** `feat/da-insire-enterprise` @ `57c9541` (+14 commits vs master `c7338c9`)

---

## B — Background

Enterprise Design Agent / INSPIRE Three-Brain pipeline parked during COI Marketing M2.
Git merge-tree vs master: **no file conflicts**; **zero overlap** with M2 publishers/commander-ui.
Soft overlap: `api/app.py`, `core/models.py`.

---

## L — Limitations

- Local stash `WIP inspire engine safety retry` must be reviewed vs `agent/inspire/engine.py`
- Split-brain risk with `feat/design-agent-v31` — do not mix
- Zasada 11 — no autonomous prod deploy
- Do not mix with COI ops mid-session

---

## A — Implementation plan (next session)

1. `/vibe-init` on `feat/da-insire-enterprise` (or worktree)
2. Review stash@{0} inspire safety vs enterprise `engine.py`
3. Rebase/merge master (`c7338c9`+) into feature branch
4. Run INSPIRE pytest suite (10 files on branch)
5. Merge → `master` after Dowódca approve
6. Deploy checklist (manual) + smoke design-agent API

---

## S — Success criteria

- [ ] Stash resolved or discarded with reason
- [ ] Feature branch includes current master
- [ ] INSPIRE unit tests green
- [ ] Merge commit on master
- [ ] Deploy PROOF handoff (after Dowódca go)

---

## V-FILES

1. `todo.json`
2. `docs/handoffs/2026-07-17-restore-footing.md`
3. `docs/handoffs/2026-07-17-coi-content-intake-m2-DEPLOY-PROOF.md`
4. `agent/inspire/engine.py` (on feature branch)

---

```
BLAST_ANCHOR: docs/handoffs/2026-07-17-da-insire-enterprise-merge-blast.md
BACKLOG_ID: DA-INSIRE-ENTERPRISE-MERGE
RECOMMENDED_NEXT: /vibe-init after FB token OK (or parallel if Marketing publish not needed)
```
