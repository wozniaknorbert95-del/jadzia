---
description: L2 - Atomic Implementation Engine.
---

# /implement

## 🎯 Goal
Translate the `/blast` or `/blueprint` into production-ready code using atomic changes to minimize cognitive load and prevent regressions.

## 🛠️ Procedure

### 1. Anchor Sync
- Read the `BLAST_ANCHOR` or `BLUEPRINT_MAP`.
- Verify that the current state of the code matches the assumptions in the plan.

### 2. Atomic Execution (The "Surgical" Method)
DO NOT rewrite entire files. Use the following cycle for each change:
1. **Target**: Identify the exact lines/functions to change.
2. **Surgical Edit**: Use `edit_file` with precise `old_text` and `new_text`.
3. **Local Verify**: Check for syntax errors or obvious logic breaks.
4. **Commitment**: Mark the step as completed in the BLAST checklist.

### 3. Pipeline Alignment
Synchronize the implementation with the Jadzia-Core internal pipeline:
- `planning` $\to$ `reading_files` $\to$ `generating_code` $\to$ `diff_ready`.
- Ensure that any changes to the `Worker loop` (api/app.py) preserve the 15s/2s polling logic and the 600s timeout.

### 4. Self-Verification
Before declaring `DIFF_READY`, check:
- [ ] No `print()` statements left for debugging.
- [ ] Type hints are consistent with `mypy` expectations.
- [ ] Docstrings updated to reflect changes.
- [ ] No secrets/keys leaked in the code.

## 📤 Output Format

```text
IMPLEMENTATION_STATUS: [IN_PROGRESS | DIFF_READY]
FILES_TOUCHED: [List of files]
CHANGES_MADE: [Summary of atomic edits]
VERIFICATION_CHECK: [PASS | FAIL]

---
CURRENT_STAGE: L2-Execute
RECOMMENDED_NEXT: /jadzia-test
WHY_NEXT: Code implemented; needs automated validation.
---
```
