# ⚙️ Jadzia-Core Workflow Framework v2.0 (Elite Edition)

This is the professional operating system for AI agents working on the Jadzia-Core project. It transforms the agent from a "chat assistant" into a "software engineer" by enforcing a strict, state-based pipeline.

## 🗺️ The Golden Path (Execution Flow)

Every task MUST follow this sequence. Skipping stages is only allowed for `HOTFIX` or `PANIC` classifications.

`L0: TRIAGE` $\xrightarrow{}$ `L1: DESIGN` $\xrightarrow{}$ `L2: EXECUTE` $\xrightarrow{}$ `L3: VALIDATE` $\xrightarrow{}$ `L4: RELEASE`

### 🛠️ Command Matrix

| Layer | Command | Purpose | Key Artefact | Gate |
| :--- | :--- | :--- | :--- | :--- |
| **L0** | `/vibe-init` | Triage, Classification, Context Loading | `TASK_ID` / `PATH` | Path Selection |
| **L0** | `/context-reset` | Memory purge for fresh start/pivot | `CLEAN_SLATE` | Ready for Init |
| **L1** | `/blast` | Technical contract for NEW features | `BLAST_ANCHOR` | `/self-review` $\to$ Approval |
| **L1** | `/blueprint` | Structural design for Refactors/Arch | `BLUEPRINT_MAP` | `/self-review` $\to$ Approval |
| **L1** | `/migrate` | High-risk DB schema/data changes | `MIG_VERSION` | Backup $\to$ Validation |
| **L1** | `/dep-audit` | Library/Dependency gatekeeper | `DEP_VERDICT` | Approval |
| **L2** | `/implement` | Atomic code implementation | `DIFF_READY` | Self-Verification |
| **L2** | `/debug` | Scientific Root-Cause Analysis (RCA) | `ROOT_CAUSE` | Fix Proposal |
| **L2** | `/profile` | Performance tuning & bottleneck hunt | `PERF_GAIN` | Measure $\to$ Verify |
| **L3** | `/jadzia-test` | Automated Pytest & Smoke tests | `TEST_PASS` | Green Pipeline |
| **L3** | `/audit-red-team` | Adversarial check & Regression audit | `VERDICT: PASS` | Safety Clear |
| **L4** | `/jadzia-deploy` | Bare-metal VPS deployment runbook | `DEPLOY_DONE` | Commander Confirmed |
| **L4** | `/handoff` | State sync (todo.json, brain.md) | `SESSION_CLOSED` | Archive |
| **L-CRIT**| `/panic` | Emergency restore (Production Down) | `SYSTEM_UP` | Post-Mortem $\to$ `/debug` |

## 📜 Core Engineering Rules

1. **The 1-1-1 Rule**: One task, one change, one handoff. No "while I'm here" changes.
2. **Zasada 11 (Commander-Only)**: The agent NEVER executes SSH commands. It provides the block; the Commander runs it.
3. **Atomic Diffs**: Never overwrite large files blindly. Use search-and-replace blocks to preserve surrounding logic.
4. **State Persistence**: Every session must start by reading `todo.json` and `brain.md` and end by updating them.
5. **Invariant Protection**: Before any change, identify the "Invariants" (things that MUST NOT break).
6. **Adversarial Thinking**: No `/blast` is complete without a `/self-review` pass.

## 📜 Core Engineering Rules

1. **The 1-1-1 Rule**: One task, one change, one handoff. No "while I'm here" changes.
2. **Zasada 11 (Commander-Only)**: The agent NEVER executes SSH commands. It provides the block; the Commander runs it.
3. **Atomic Diffs**: Never overwrite large files blindly. Use search-and-replace blocks to preserve surrounding logic.
4. **State Persistence**: Every session must start by reading `todo.json` and `brain.md` and end by updating them.
5. **Invariant Protection**: Before any change, identify the "Invariants" (things that MUST NOT break).

## 🚀 Quick Start
1. Start every session with `/vibe-init`.
2. Follow the `RECOMMENDED_NEXT` output.
3. Close every session with `/handoff`.
