---
description: L2 - Scientific Diagnostic & Root-Cause Analysis (RCA).
---

# /debug

## 🎯 Goal
Move from "guessing" to "proving". Identify the exact line and state that causes a failure and propose a surgical fix.

## 🛠️ The 5-Step Scientific Method

### Step 1: Evidence Collection
- **Symptom**: What is the exact error? (Stack trace, log line, incorrect API response).
- **Environment**: Local vs VPS, Telegram vs HTTP.
- **Determinism**: Is it reproducible 100% of the time or intermittent?

### Step 2: Isolation (Hypothesis Generation)
Isolate the failure to a specific layer:
- **Layer 1 (Interface)**: `api/app.py`, `api/routes/`, `api/telegram.py`.
- **Layer 2 (Logic)**: `core/services.py` or `agent/agent.py`.
- **Layer 3 (State)**: `agent/state/` or `agent/db.py`.
- **Layer 4 (External)**: Anthropic API, Telegram API, SQLite locks.

### Step 3: Proof of Concept (The "Smoking Gun")
Prove the hypothesis.
- **Method**: Create a minimal reproduction script (`tests/repro_bug.py`) or a specific `curl` command.
- **Result**: "When I call X with input Y, I get error Z. This confirms the bug is in `function_a`."

### Step 4: Root Cause Analysis (RCA)
Define the *why*:
- "The worker loop fails because the SQLite lock timeout (30s) is shorter than the processing time of large tasks (600s)."

### Step 5: Surgical Proposal
Propose the fix and the verification plan:
- **Fix**: Change `lock_timeout` to 610s.
- **Verify**: Run `repro_bug.py` $\to$ PASS.

## 📤 Output Format

```text
ISSUE: [Brief description]
EVIDENCE: [Log/Stacktrace]
HYPOTHESIS: [Where the bug is]
PROOF: [Reproduction steps/result]
ROOT_CAUSE: [The "Why"]
PROPOSED_FIX: [Surgical change]

---
CURRENT_STAGE: L2-Debug
RECOMMENDED_NEXT: /implement
WHY_NEXT: Root cause proven; fix ready for execution.
---
```
