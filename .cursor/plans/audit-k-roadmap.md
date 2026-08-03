---
status: ACTIVE
created: "2026-08-03"
updated: "2026-08-03"
origin: "Expert Audit 3-panel (Agency Owner + AI Systems Engineer + UX/UI)"
canonical_register: "docs/ops/demand-os/AUDIT-K-REGISTER.md"
truth_rule: "DONE only with code + tests + required runtime/prod evidence"
sprint_model: "S1 = K2+K4 → S2 = K1+K3 → S3 = K5–K9 → S4 = K10–K14"
---

# Audit K-Roadmap — Demand Desk Revenue Path

> **Truth:** K2 and K4 are **partial**, not done. See [`AUDIT-K-REGISTER.md`](../../docs/ops/demand-os/AUDIT-K-REGISTER.md).

## Context

Expert audit scored:
- Agency Owner: biznes **3/10**, architektura **8/10** → revenue gap
- AI Systems Engineer: solid HITL, SQLite OK, dual SoT risk
- UX/UI Specialist: 8 views, jargon wall, auth friction

F1–F7 UX repair already deployed (desk-dash09). This roadmap covers the **K-items**.

## K-Items

### Sprint S1 (in progress — honesty recovery)

| ID | Item | Status | DoD |
|----|------|--------|-----|
| **K2** | GA4 adapter → desk signal | `partial` | Split sessions/starts/UTM; fail-closed `unavailable`; live fixture tests; VPS proof after GO — **not done while stub shows —** |
| **K4** | Plain-language labels | `partial` | Zero internal jargon on primary surface; copy tests; desktop/375 evidence after deploy — **not done while empty states say HITL/JSON paths** |

### Sprint S2 (next)

| ID | Item | Status | DoD |
|----|------|--------|-----|
| **K1** | REV_R1 attribution | `not_started` | Real `wizard_start` event → SQLite → export → desk with trace ID |
| **K3** | Auth simplify | `not_started` | Founder session without manual JWT paste; no token in URL; revoke works |

### Sprint S3 (tech debt — essential)

| ID | Item | Status | DoD |
|----|------|--------|-----|
| **K5** | Dual SoT reconcile | `not_started` | SQLite authority; files = projection; dry-run drift |
| **K6** | View consolidation | `not_started` | Desk eager; other views lazy + inert |
| **K7** | Mobile-first desk CSS | `not_started` | 320/375/390 no overflow; CTA clickable |
| **K8** | Accessibility baseline | `not_started` | axe Critical/Serious = 0 |
| **K9** | Performance baseline | `not_started` | LCP/CLS/INP budgets + 3 traces |

### Sprint S4 (tech debt — quality)

| ID | Item | Status | DoD |
|----|------|--------|-----|
| **K10** | Error UX | `not_started` | Typed errors; no raw JSON on primary |
| **K11** | Offline/cache resilience | `not_started` | Cached read + timestamp; no mutation replay |
| **K12** | Desk test coverage | `not_started` | ≥80% line / ≥70% branch on desk modules |
| **K13** | Ledger auto-export | `not_started` | Deterministic export from SQLite + manifest |
| **K14** | Deploy automation | `not_started` | Validate-only; deploy blocked without GO |

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| GA4 stub = empty desk signal | Desk looks dead | Finish K2 honestly; then K1 |
| Dual SoT drift | Data inconsistency | K5 |
| Auth friction | Founder doesn't return | K3 |
| Fake DONE labels | Trust collapse | AUDIT-K-REGISTER + evidence rule |

## Rules

- Live P0 (TT/FB/blog publish) stays **PARKED** until Dowódca unlock
- No VPS deploy without GO
- Never mark DONE without evidence in AUDIT-K-REGISTER
