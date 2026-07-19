---
description: L1-Review - Adversarial Internal Audit.
---

# /self-review

## 🎯 Goal
Act as a "Critical Senior Engineer" to find flaws in the `/blast` or `/blueprint` before implementation begins. This is the "Zero-Bug" filter.

## 🛠️ The "Devil's Advocate" Checklist

### 1. Logic Gaps
- "What happens if the LLM returns a malformed JSON here?"
- "Is there a race condition between the worker loop and the API endpoint?"
- "Does this design assume the user always provides X, but they might provide Y?"

### 2. Complexity Audit
- "Is this over-engineered? Can we achieve 90% of the result with 10% of the code?"
- "Does this introduce a new dependency that we don't really need?"

### 3. Regression Risk
- "Which existing feature is most likely to break because of this change?"
- "Does this change affect the `jadzia.db` schema in a way that makes rollback impossible?"

### 4. Invariant Check
- "Does this violate any of the core rules in `brain.md`?"

## 🏁 Verdict
- **APPROVED**: Plan is solid.
- **REVISE**: Specific flaws found. Return to `/blast` or `/blueprint`.

## 📤 Output Format

```text
REVIEW_VERDICT: [APPROVED | REVISE]
CRITICAL_FLAWS: [List of issues found | NONE]
SUGGESTED_IMPROVEMENTS: [List]
RISK_SCORE: [1-10]

---
CURRENT_STAGE: L1-Review
RECOMMENDED_NEXT: [/implement | /blast]
---
```
