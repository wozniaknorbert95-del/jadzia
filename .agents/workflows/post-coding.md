---
description: L3.5 - Post-coding drain (validate → ship → release → evidence → handoff).
---

# /post-coding

## Goal

Drain one `todo.active_gate` from green code/docs to **evidence + handoff** without Dowódca micro-clicks.
Deploy is **inside** this stage when `todo.standing_go_closeout === true` or GO is already recorded in-session.

## Preconditions

- BLAST/DoD for the gate exists (or thin ritual checklist for ops-only gates).
- Hard STOP still applies: Gate D, Mollie LIVE, secret rotation, merge OS↔jadzia, fake PASS.

## Procedure (one gate)

### 1. Anchor

- Read `todo.json`: `active_gate`, `closeout_queue`, `standing_go_closeout`.
- Confirm gate matches queue head (or explicit override recorded in handoff).

### 2. Validate

- Scoped pytest / smoke for touched surface.
- FAIL → `/debug`, do **not** ship.

### 3. Ship

- Commit + push (no secrets, no `deployment/_mint_*`, no `_recover_*`).
- Message focuses on why (gate + evidence intent).

### 4. Release

When prod tip must move:

| Condition | Action |
|-----------|--------|
| `standing_go_closeout` or in-session GO | Agent runs VPS: backup (if runtime) → `git pull --ff-only` → restart **only if runtime code changed** → `/health` |
| No GO | Emit COMMAND_BLOCK only; status `AWAIT_COMMANDER` |

Canonical script: `deployment/rev-demand-01-deploy-vps.sh` (runtime). Docs-only tip sync: `git pull --ff-only` without restart.

### 5. Evidence

- Number, URL, or dogfood path in scorecard / handoff.
- **Never** mark `completed` without evidence.

### 6. Handoff

- `docs/handoffs/YYYY-MM-DD-<gate>-CLOSE.md` (or PARK).
- Update `todo.json`, `AGENTS.md`, scorecard if status changed.
- Pop gate from `closeout_queue`; set `active_gate` to next head (or null on CLOSEOUT_DONE).

### 7. Continue-or-park

- Next gate agent-capable → start it (or Automation next run).
- Human-only (e.g. Basic Auth) → `ready_for_human` + checklist; **zero A/B questions**.

## Output

```text
POST_CODING: PASS|FAIL|PARK
GATE: COI-…
EVIDENCE: …
TIP: …
NEXT_GATE: … | CLOSEOUT_DONE
HUMAN_CLICKS_NEEDED: 0 | 1 (auth/budget only)

---
CURRENT_STAGE: L3.5-PostCoding
RECOMMENDED_NEXT: /post-coding (next gate) | /handoff | ready_for_human
WHY_NEXT: …
---
```
