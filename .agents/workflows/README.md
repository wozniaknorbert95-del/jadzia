# Jadzia-Core Workflow Framework v2.2 (Golden Path)

Professional operating system for agents on jadzia-core: state-based pipeline, 1-1-1, honest PASS.

## Golden workflows (this folder only)

| File | Command | Layer | Purpose |
| :--- | :--- | :--- | :--- |
| `vibe-init.md` | `/vibe-init` | L0 | Triage + context |
| `jadzia-test.md` | `/jadzia-test` | L3 | Pytest + smoke |
| `vhq-decision-instrument.md` | `/vhq-decision-instrument` | L3–L4 | Scorecard S1–S8 → 5/5 (tests + dogfood) |
| `post-coding.md` | `/post-coding` | L3.5 | Validate→ship→evidence |
| `jadzia-deploy.md` | `/jadzia-deploy` | L4 | VPS release (or pack if no GO) |
| `handoff.md` | `/handoff` | L4 | State sync |
| `panic.md` | `/panic` | L-CRIT | Prod down |
| `demand-os-execute.md` | `/demand-os-execute` | L2 ops | Demand Machine step runner (SET NOW→W1→build gates) |

Non-golden workflows (blast, blueprint, migrate, debug, …) live in `.agents/archive/workflows/`.

## Golden Path

```text
L0 TRIAGE → L3 VALIDATE → L3.5 POST-CODING → L4 HANDOFF
```

**Decision Instrument program** (when `todo.closeout_queue` has `VF-VHQ-DI-*`):

```text
L0 → /vhq-decision-instrument (one S* gate) → /jadzia-test → /post-coding → GO DEPLOY → dogfood → scorecard bump → next S*
```

Skipping stages only for `HOTFIX` / `PANIC`. During AI OS closeout, `/post-coding` may include deploy when `standing_go_closeout` is true.

## Core rules

1. **1-1-1**: one gate, one change set, one handoff per drain step.
2. **Zasada 11 (deploy authority):**
   - Agent **executes** VPS when `todo.standing_go_closeout === true` **or** GO is recorded in-session.
   - Otherwise agent emits COMMAND_BLOCK only; Commander runs it.
   - Hard STOP without separate GO: Gate D, Mollie LIVE, secret rotation, OS↔jadzia merge, fake PASS.
3. **Atomic diffs** — surgical edits; no blind whole-file rewrites.
4. **State persistence** — start: `todo.json` + `brain.md`; end: handoff.
5. **Invariants** — name what must not break before editing.
6. **Honesty** — no PASS/completed without dogfood number or URL evidence.
7. **No-ask (Dowódca)** — one path, execute; park human-only as `ready_for_human`.
8. **SQLite only** — single DB path `data/jadzia.db`; inline migrations in `agent/db.py`.

## Quick start

1. `/vibe-init`
2. Follow `RECOMMENDED_NEXT`
3. After green tests: `/post-coding`
4. `/handoff` when parking or CLOSEOUT_DONE
