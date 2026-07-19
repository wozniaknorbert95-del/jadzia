---
description: L1-Audit - Dependency & Library Gate.
---

# /dep-audit

## 🎯 Goal
Prevent "Dependency Hell" and security vulnerabilities by strictly auditing every new library added to the project.

## 🛠️ Audit Criteria

### 1. Necessity Test
- Can this be implemented using the Python Standard Library in < 50 lines?
- Does this library overlap with an existing dependency?

### 2. Weight & Bloat
- What is the installation size?
- Does it pull in 20 other transitive dependencies?

### 3. Health & Security
- **Maintenance**: Last commit date? Number of open critical issues?
- **Security**: Check for known CVEs.
- **License**: Is the license compatible with the project?

### 4. Integration Risk
- Does it conflict with our current versions of `pydantic` or `fastapi`?
- Does it introduce any blocking I/O that could hang the worker loop?

## 📤 Output Format

```text
LIB_NAME: [package_name]
VERDICT: [APPROVE | REJECT | FIND_ALTERNATIVE]
JUSTIFICATION: [Reasoning]
RISK_ASSESSMENT: [Low | Med | High]

---
CURRENT_STAGE: L1-Audit
RECOMMENDED_NEXT: /implement (to add to requirements.txt)
---
```
