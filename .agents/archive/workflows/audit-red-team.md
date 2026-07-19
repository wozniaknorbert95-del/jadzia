---
description: L3 - Adversarial Audit & Regression Analysis.
---

# /audit-red-team

## 🎯 Goal
Think like an attacker or a "chaos monkey". Attempt to break the implementation and find edge cases that `pytest` missed.

## 🛠️ Audit Checklist

### 1. Security & Least Privilege
- **Secrets**: Are there any API keys or passwords hardcoded in the diff?
- **Paths**: Does the new code allow reading/writing files outside the allowed scope (Check `agent/guardrails.py`)?
- **Permissions**: Does the code assume `root` privileges that might be restricted later?

### 2. Stability & Edge Cases
- **Nulls/Empty**: What happens if the API returns an empty list or `None`?
- **Concurrency**: What happens if two worker loops try to access the same SQLite session?
- **Timeouts**: Does a slow external API call (Anthropic/WooCommerce) hang the entire worker loop?

### 3. Regression Audit
- Does this change affect any existing feature in `brain.md`?
- If a module was split (Refactor), do all existing imports still work?

## 🏁 Verdict
- **PASS ✅**: No critical vulnerabilities or regressions found.
- **FAIL ❌**: Critical risk identified. Must return to `/implement` or `/debug`.

## 📤 Output Format

```text
VULNERABILITIES: [List of risks found | NONE]
EDGE_CASES_TESTED: [List of scenarios]
REGRESSION_RISK: [Low | Med | High]
VERDICT: [PASS ✅ | FAIL ❌]

---
CURRENT_STAGE: L3-Audit
RECOMMENDED_NEXT: [/jadzia-deploy | /implement]
WHY_NEXT: PASS $\to$ Ready to ship; FAIL $\to$ Fix required.
---
```
