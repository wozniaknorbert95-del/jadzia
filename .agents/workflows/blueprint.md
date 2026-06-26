---
description: L1 - Structural & Architectural Mapping. Used for Refactors and Migrations.
---

# /blueprint

## 🎯 Goal
Map the structural transformation of the system. Unlike `/blast` (which adds), `/blueprint` focuses on **reorganizing** while preserving behavior (Behavior-Preserving Transformation).

## 🛠️ Procedure

### 1. Current State Analysis (As-Is)
- Map the existing coupling. (e.g., "`agent/agent.py` is currently tightly coupled to `agent/state.py` via X method").
- Identify "God Objects" or "Leaky Abstractions".

### 2. Target State Design (To-Be)
- Define the new module boundaries.
- Create a dependency graph: `Module A` $\to$ `Module B` $\to$ `Persistence`.
- Specify the API contract between the new modules.

### 3. Migration Strategy (The Transition)
Define how to move from As-Is to To-Be without breaking the system:
- **Phase 1**: Shadow implementation (new code runs alongside old).
- **Phase 2**: Traffic shift (new code takes over).
- **Phase 3**: Deletion of legacy code.

### 4. Regression Guardrails
- Identify the "Golden Suite" of tests that MUST pass to prove no behavior changed.
- Define the "Emergency Rollback" path (e.g., "Revert symlink to previous release").

## 📤 Output Format

```text
BLUEPRINT_ID: [Refactor-X]
CURRENT_COUPLE: [Source] -> [Target]
TARGET_STRUCTURE: [New Module Map]
MIGRATION_STEPS: [Phase 1, 2, 3]
REGRESSION_TESTS: [List of critical tests]

---
CURRENT_STAGE: L1-Architecture
RECOMMENDED_NEXT: /implement (Awaiting Commander Approval)
WHY_NEXT: Structural map complete; risk minimized.
---
```
