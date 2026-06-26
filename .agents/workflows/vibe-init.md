---
description: L0 - Triage & Context Router. The entry point for every session.
---

# /vibe-init

## 🎯 Goal
Map the current state, load canonical knowledge, and route the task to the correct engineering path.

## 📥 Input
- Problem Statement / Ticket / User Request.
- Optional: Reference to `todo.json` task ID.

## 🛠️ Agent Procedure

### 1. Context Loading (Hydration)
You MUST read the following files before proceeding:
- `todo.json` $\to$ Identify current task status and backlog.
- `brain.md` $\to$ Sync with project architecture and global rules.
- `AGENTS.md` $\to$ Review guardrails.
- (Optional) Last 2 files from `docs/handoffs/` to maintain continuity.

### 2. Task Classification
Classify the request into one of the following paths:

| Signal | CLASSIFICATION | PATH | LOGIC |
| :--- | :--- | :--- | :--- |
| New logic, API, agent node, Feature | **FEATURE** | `L1: /blast` $\to$ `/self-review` | Requires a technical contract. |
| Structural change, module split, tech debt | **REFACTOR** | `L1: /blueprint` $\to$ `/self-review` | Requires impact mapping. |
| Bug, regression, unexpected behavior | **BUGFIX** | `L2: /debug` | Requires Root-Cause Analysis. |
| Known fix, critical outage, trivial change | **HOTFIX** | `L2: /implement` | Fast-track to execution. |
| DB Schema change / Alembic | **MIGRATE** | `L1: /migrate` | High-risk persistence change. |
| Push to Production | **DEPLOY** | `L3: /jadzia-test` $\to$ `L4: /jadzia-deploy` | Release pipeline. |
| Production DOWN / Critical Failure | **CRITICAL** | `L-CRIT: /panic` | Emergency restoration. |
| Perf issues, Slow queries, Latency | **PERF** | `L2: /profile` | Performance engineering. |
| New Library / Package | **DEP** | `L1: /dep-audit` | Dependency gatekeeping. |

### 3. Constraint Mapping
Identify:
- **Invariants**: What must stay exactly as is?
- **Dependencies**: Which modules (`core/services.py`, `agent/state/`) are touched?
- **Risks**: Potential side effects on the worker loop or SQLite locks.

## 📤 Output Format

```text
TASK_CLASSIFICATION: [FEATURE | REFACTOR | BUGFIX | HOTFIX | MIGRATE | DEPLOY]
TASK_ID: [ID from todo.json | NEW]
CONSTRAINTS: [...]
INVARIANTS: [...]
RISKS: [...]
READY: [YES | NO - Missing: X]

---
CURRENT_STAGE: L0-Triage
RECOMMENDED_NEXT: [/blast | /blueprint | /debug | /implement | /jadzia-test | /jadzia-deploy]
WHY_NEXT: [Brief engineering justification]
---
```
