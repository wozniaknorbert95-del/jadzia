# Jadzia-Core Workflow Framework v2.1

Professional operating system for agents on jadzia-core: state-based pipeline, 1-1-1, honest PASS.

## Golden Path

```text
L0 TRIAGE → L1 DESIGN → L2 EXECUTE → L3 VALIDATE → L3.5 POST-CODING → L4 HANDOFF
```

Skipping stages only for `HOTFIX` / `PANIC`. During AI OS closeout, `/post-coding` may include deploy when `standing_go_closeout` is true.

### Command matrix

| Layer | Command | Purpose | Key artefact |
| :--- | :--- | :--- | :--- |
| **L0** | `/vibe-init` | Triage + context | `TASK_ID` |
| **L0** | `/context-reset` | Clean slate | `CLEAN_SLATE` |
| **L1** | `/blast` | Feature contract | `BLAST_ANCHOR` |
| **L1** | `/blueprint` | Refactor design | `BLUEPRINT_MAP` |
| **L1** | `/migrate` | DB risk | `MIG_VERSION` |
| **L1** | `/dep-audit` | Dependency gate | `DEP_VERDICT` |
| **L2** | `/implement` | Atomic code | `DIFF_READY` |
| **L2** | `/debug` | RCA | `ROOT_CAUSE` |
| **L2** | `/profile` | Perf | `PERF_GAIN` |
| **L3** | `/jadzia-test` | Pytest + smoke | `TEST_PASS` |
| **L3** | `/audit-red-team` | Adversarial | `VERDICT` |
| **L3.5** | `/post-coding` | Validate→ship→release→evidence→handoff | `POST_CODING` |
| **L4** | `/jadzia-deploy` | VPS release (or pack if no GO) | `DEPLOY_DONE` |
| **L4** | `/handoff` | State sync | `SESSION_CLOSED` |
| **L-CRIT** | `/panic` | Prod down | `SYSTEM_UP` |

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

## Closeout loop

When `standing_go_closeout` is set, drain `closeout_queue` via `/post-coding` (agent or Cursor Automation **Jadzia AI-OS Post-Coding Closeout**). After `AI-OS-CLOSEOUT`, set `standing_go_closeout: false`.

## Quick start

1. `/vibe-init`
2. Follow `RECOMMENDED_NEXT`
3. After green tests: `/post-coding` (not a separate click for deploy during closeout)
4. `/handoff` when parking or CLOSEOUT_DONE
