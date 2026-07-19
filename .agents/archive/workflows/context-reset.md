---
description: L0 - Memory Purge & Context Reset.
---

# /context-reset

## 🎯 Goal
Clear the agent's active working memory (context window) to prevent "context pollution" when switching between unrelated tasks.

## 🛠️ Procedure

### 1. State Archive
Before resetting, ensure the current state is captured in `/handoff`.
- [ ] `todo.json` updated.
- [ ] `brain.md` updated.
- [ ] Handoff file written.

### 2. Memory Purge
The agent should explicitly notify the user that it is discarding the current conversation history regarding the specific implementation details of the previous task.

### 3. Re-Initialization
Immediately trigger `/vibe-init` for the next task to reload only the necessary canonical knowledge.

## 📤 Output Format

```text
CONTEXT_STATUS: PURGED
ARCHIVE_CONFIRMED: [YES | NO]
READY_FOR: /vibe-init [Next Task ID]

---
CURRENT_STAGE: L0-Reset
RECOMMENDED_NEXT: /vibe-init
WHY_NEXT: Fresh context prevents hallucinations and drift.
---
```
