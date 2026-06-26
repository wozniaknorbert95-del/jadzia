---
description: L1 - Technical Contract for NEW Features.
---

# /blast

## 🎯 Goal
Create a durable, immutable technical contract before a single line of code is written. This prevents "vibe-drift" and ensures the implementation matches the design.

## 🛠️ Procedure

### 1. B - Background (The "Why")
- Link to `todo.json` task ID.
- Define the user-facing value and the internal technical trigger.
- Map the data flow: `User Request` $\to$ `API` $\to$ `Service` $\to$ `State/DB`.

### 2. L - Limitations & Boundary Conditions
- **Performance**: Max latency, SQLite lock duration.
- **Security**: Which guardrails in `agent/guardrails.py` apply?
- **Infrastructure**: Bare-metal VPS constraints, memory limits.

### 3. A - Actions (The Implementation Roadmap)
Detailed checklist of files to be modified/created:
- [ ] `core/services.py`: Add method `X`.
- [ ] `api/routes/X.py`: Add endpoint `Y`.
- [ ] `agent/state.py`: Update schema for `Z`.
- [ ] `tests/`: Create `test_feature_x.py`.

### 4. S - Success Criteria (Definition of Done)
Binary conditions for success:
- [ ] `pytest` passes for the new module.
- [ ] `/health` endpoint remains green.
- [ ] Telegram/HTTP response matches the expected schema.

### 5. T - Test Plan
- **Unit**: Which functions need isolated testing?
- **Integration**: How to test the flow from API to DB?
- **Smoke**: Manual verification steps.

## ⚓ Anchor
Save this plan to `.cursor/current-task.md` or `docs/handoffs/YYYY-MM-DD-feature-blast.md`.

## 📤 Output Format

```text
BLAST_ANCHOR: [path/to/file]
BACKLOG_ID: [ID]
INVARIANTS_TO_PROTECT: [...]
SUCCESS_CRITERIA: [Binary Checklist]
IMPLEMENTATION_PLAN: [Step-by-step files]

---
CURRENT_STAGE: L1-Design
RECOMMENDED_NEXT: /implement (Awaiting Commander Approval)
WHY_NEXT: Technical contract established.
---
```
