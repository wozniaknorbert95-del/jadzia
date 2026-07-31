---
status: "[PRE-CLOSE · HITL]"
title: "VF-CAMPUS-W3 — Truth Cards pilot Pre-Close"
gate: "VF-CAMPUS-W3"
updated: "2026-07-27"
cache: "campus-w03"
prod_baseline_w2: "df3d59a · ?v=campus-w01 (LIVE)"
w3_on_prod: false
commit: false
deploy: false
w4_started: false
---

# W3 Pre-Close — Truth Cards pilot×5

## Prod verify (prerequisite) — PASS

| Check | Result |
|-------|--------|
| Public Commander HTTP | **200** |
| Tip expected | **df3d59a** (W2 badges) |
| Markers | EV-W2-001 / 005 / 006 / 009 present · no EV-002 |
| Worker health | **degraded** SSH · EV-W2-011 / INC-SSH-RECOVERY-00 |

## GO VF-CAMPUS-W3 — implemented (source)

| Item | Status |
|------|--------|
| `active_gate` | **VF-CAMPUS-W3** `in_progress` |
| 5 Truth Cards on Home | `#truth-cards-pilot` |
| Cache | **`campus-w03`** (CSS/JS/MC hop) |
| 6th tab | **none** (5 primary) |
| app.js logic | **unchanged** |
| Fake KPI / fake 0 | **none** — `insufficient_data` / PARKED freeze |
| MKT assets / Ads | **none** |

### Pilot cards

| Room | Status on card | Evidence / honesty |
|------|----------------|--------------------|
| Mission Control | LIVE | EV-W2-001 · worker DEGRADED called out |
| Sales / Wizard | LIVE | EV-W2-005 · wizard_starts = insufficient_data |
| Marketing Studio | NO ACTIVE CAMPAIGN | parked_by_founder · CPA PARKED freeze |
| Order Desk | PARKED | EV-W2-010 · open orders insufficient_data |
| Finance | UNVERIFIED | EV-W2-008 · Analityka path · session needed |

## Local validation

`W3_LOCAL_VALIDATION_PASS` · `TODO_OK VF-CAMPUS-W3 in_progress`

## Files (W3 scope)

- `commander-ui/index.html`
- `commander-ui/styles.css`
- `todo.json`
- `docs/ops/FLEXGRAFIK-CAMPUS-PROGRAM.md`
- this handoff

## HITL stop

**Not closed. Not committed. Not deployed.**

Recommended next:
```text
CLOSE VF-CAMPUS-W3
```
then commit → deploy `campus-w03` → prod verify → (W4 only after C2 GO).
