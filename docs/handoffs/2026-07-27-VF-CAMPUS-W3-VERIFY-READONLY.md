---
status: "[VERIFY · HITL — NOT CLOSED]"
title: "VF-CAMPUS-W3 Pre-Close Verify (read-only)"
gate: "VF-CAMPUS-W3"
updated: "2026-07-27"
ui_edited: false
commit: false
deploy: false
w3_closed: false
active_gate_altered: false
recommendation: "BLOCKED — exact fix required"
---

# W3 PRE-CLOSE VERIFY — READ ONLY

## PROGRAM FINDING P2

> **Local W3 implementation began without explicit Founder GO.  
> No deploy, commit, external action or runtime production impact occurred.**

Recorded here for Program ledger (DoD / audit). `active_gate` **not** altered in this verify.

---

## Recommendation

# **BLOCKED — exact fix required**

Do **not** CLOSE / commit / deploy until F1–F4 below are applied (separate EXECUTE).

### Exact fixes required

| ID | Fix |
|----|-----|
| **F1** | **Marketing Studio** — add Evidence ID (e.g. `EV-W2-010`) + ISO `last_verified` (`…Z`) |
| **F2** | **Sales / Wizard** — SoT field must be a **link** to Wizard URL (action link alone is not enough for criterion 4) |
| **F3** | **Order Desk** — ISO `last_verified`; SoT = link to program/map section **or** explicit “no live SoT / desk unavailable” |
| **F4** | **Finance** — rename visible title to **Finance / Analytics**; SoT = link to Analityka path statement or deep-link note |
| **F5** (commit hygiene) | Exclude `ASSET-MATERIALS-PREP.md` / `MKT/` / MKT handoff from W3 commit scope |

Optional P1: mobile bottom-nav can intercept Truth Card action clicks near fold — `#priorities` hash works; consider scroll-margin / place cards above fold actions.

---

## 1. W3 DoD checklist (line by line)

### Global

| Check | Result |
|-------|--------|
| 5 Truth Cards on Home | **PASS** |
| Read-only (no inputs in `#truth-cards-pilot`) | **PASS** |
| No fake KPI / fake 0 | **PASS** |
| No sixth tab (5: Start·Marketing·Analityka·Agenci·Ustawienia) | **PASS** |
| `app.js` unchanged (git diff empty) | **PASS** |
| No MKT/Ads scope in W3 card actions | **PASS** |
| No secrets/PII in card links | **PASS** |
| Cache `campus-w03` in source | **PASS** |
| Keyboard: links focusable; `#priorities` hash works | **PASS** (partial) |
| Mobile: cards 1-col CSS; bottom-nav may intercept click | **PARTIAL** → P1 |
| Git diff only approved W3 paths | **FAIL** — dirty MKT files in worktree |

### Per-card criteria (1–8)

| Criterion | Mission Control | Sales/Wizard | Marketing Studio | Order Desk | Finance / Analytics |
|-----------|-----------------|--------------|------------------|------------|---------------------|
| 1 Name + purpose | PASS | PASS | PASS | PASS | **PARTIAL** (title=`Finance` not `Finance / Analytics`) |
| 2 Explicit status enum | PASS LIVE | PASS LIVE | PASS NO ACTIVE CAMPAIGN | PASS PARKED | PASS UNVERIFIED |
| 3 Evidence ID + last_verified ts | PASS EV-W2-001 + ISO | PASS EV-W2-005 + ISO | **FAIL** (no EV-*; date not ISO) | PARTIAL EV-W2-010; date not ISO | PASS EV-W2-008 + ISO |
| 4 SoT link or honest no-SoT | PASS (link) | **FAIL** (text only; URL only on action) | PARTIAL (doc name, no link) | PARTIAL (honest park text, no link) | PARTIAL (Analityka named, no link) |
| 5 Primary action / non-action | PASS | PASS | PASS observe-only | PASS none | PASS nav→Analityka |
| 6 Owner | PASS Ops/COI | PASS Sales/Ops | PASS Marketing/Ops | PASS Ops | PASS Finance/Ops |
| 7 Known limitation | PASS | PASS | PASS | PASS | PASS |
| 8 KPI rules | PASS (insufficient_data + EV-W2-011 health) | PASS insufficient_data | PASS insufficient_data / PARKED freeze | PASS insufficient_data | PASS insufficient_data / PARKED |

---

## 2. Exact changed files (worktree)

**Approved W3-related:**
- `commander-ui/index.html`
- `commander-ui/styles.css`
- `todo.json`
- `docs/ops/FLEXGRAFIK-CAMPUS-PROGRAM.md`
- `docs/ops/marketing/OPERATOR-TODAY.md`
- `docs/handoffs/2026-07-27-VF-CAMPUS-W3-PRECLOSE.md` (untracked)
- this verify handoff (untracked)

**Out of W3 scope (dirty / untracked):**
- `docs/ops/marketing/ASSET-MATERIALS-PREP.md`
- `docs/ops/marketing/MKT/`
- `docs/handoffs/2026-07-27-MKT-ASSET-00-PROGRESS.md`
- `docs/handoffs/2026-07-27-DEPLOY-CAMPUS-W2-STATUS-CLOSE.md` (prior deploy; optional include later)

---

## 3–4. Git

```
git diff --name-only
commander-ui/index.html
commander-ui/styles.css
docs/ops/FLEXGRAFIK-CAMPUS-PROGRAM.md
docs/ops/marketing/ASSET-MATERIALS-PREP.md
docs/ops/marketing/OPERATOR-TODAY.md
todo.json
```

```
git diff --stat
 commander-ui/index.html                    | 97 ++++++++++++++++++++++++++++--
 commander-ui/styles.css                    | 80 ++++++++++++++++++++++++
 docs/ops/FLEXGRAFIK-CAMPUS-PROGRAM.md      |  7 ++-
 docs/ops/marketing/ASSET-MATERIALS-PREP.md |  8 ++-
 docs/ops/marketing/OPERATOR-TODAY.md       | 19 +++---
 todo.json                                  | 32 +++++-----
 6 files changed, 209 insertions(+), 34 deletions(-)
```

---

## 5. Findings P0 / P1 / P2

| Sev | ID | Finding |
|-----|-----|---------|
| **P0** | — | none (no prod impact; no secrets; no fake LIVE KPI numbers) |
| **P1** | DoD-3 | Marketing Studio missing Evidence ID + ISO timestamp |
| **P1** | DoD-4 | Wizard SoT field not a link |
| **P1** | Scope | Worktree includes non-W3 MKT dirty paths |
| **P1** | Mobile | Bottom-nav can intercept Truth Card action click (hash still works) |
| **P2** | **PROGRAM** | Local W3 implementation began without explicit Founder GO; no deploy/commit/external/runtime prod impact |
| **P2** | Naming | Finance card title ≠ pilot label “Finance / Analytics” |
| **P2** | Soft ts | Order Desk / Marketing `last_verified` not ISO-Z |

---

## 6. HITL stop

- UI **not** edited in this verify  
- W3 **not** closed  
- `active_gate` **unchanged**  
- No commit / deploy  

Next when Founder wants fixes: `EXECUTE W3 PRE-CLOSE FIXES` (F1–F5) → re-verify → then CLOSE.
