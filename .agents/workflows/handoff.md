---
description: L4 - Session Closure & State Synchronization.
---

# /handoff

## 🎯 Goal
Ensure the project's "canonical memory" is updated so the next agent (or session) can start without friction.

## 🛠️ Procedure

### 1. State Synchronization
Update the following files based on the session's outcome:
- **`todo.json`**: Mark tasks as `completed` or update status to `pending` for next steps.
- **`brain.md`**: Add any new architectural decisions, discovered invariants, or updated module mappings.
- **`AGENTS.md`**: Update guardrails if new ones were discovered during `/audit-red-team`.

### 2. Session Documentation
Create a handoff file in `docs/handoffs/YYYY-MM-DD-task-id.md` containing:
- **What was done**: Summary of changes.
- **What is left**: Pending items or known technical debt.
- **Critical Warnings**: "Don't touch X because it affects Y".
- **Next Step**: The exact command for the next session (e.g., `/vibe-init` for task `ADVANCED_LEAD-001`).

## 📤 Output Format

```text
STATE_SYNC: [todo.json updated | brain.md updated]
HANDOFF_FILE: [path/to/file]
NEXT_SESSION_START: [/vibe-init with TASK_ID X]
SESSION_VERDICT: [SUCCESS | PARTIAL | FAILED]

---
CURRENT_STAGE: L4-Closed
RECOMMENDED_NEXT: /context-reset (if starting new task)
WHY_NEXT: Session complete.
---
```
