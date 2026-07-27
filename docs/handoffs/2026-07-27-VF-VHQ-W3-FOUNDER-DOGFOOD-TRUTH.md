---
status: "[DOGFOOD-TRUTH]"
title: "VF-VHQ-W3 — Founder Dogfood + Truth Consistency"
updated: "2026-07-27"
gate: "VF-VHQ-W3-ROOMS-COMMERCIAL"
cache: "vhq-w03b"
local_url: "http://127.0.0.1:8765/index.html?v=vhq-w03b"
close: false
commit: false
deploy: false
w4: false
recommendation: "READY FOR FOUNDER CLOSE"
---

# VF-VHQ-W3 — Founder Dogfood + Truth Report

**Verdict:** **READY FOR FOUNDER CLOSE**  
**Cache:** `vhq-w03b`  
**Local:** http://127.0.0.1:8765/index.html?v=vhq-w03b  
**Prod tip unchanged:** `db32212` / `vhq-w02b`

---

## 1. W3 room walkthrough

| Step | Check | Result |
|------|-------|--------|
| A | Cold-open → Mission Control | **PASS** · HQ › P3 › Mission Control · SSH strip · cache vhq-w03b |
| B | Open Sales Room | **PASS** · Work View LIVE EV-W2-007 |
| C | One canonical queue only | **PASS** · `#queue-list` count = **1** · single „Kolejka” |
| D | Sales handoff → Wizard | **PASS** · strip Sales LIVE → Wizard LIVE → Order PARKED · CTA Open Wizard room |
| E | Open Wizard Room | **PASS** · in-HQ Work View |
| F | Wizard SoT + insufficient_data + Order PARKED | **PASS** · SoT wizard URL · KPI insufficient_data · Order Desk [PARKED] EV-W2-010 |
| G | Open Marketing Studio | **PASS** · honest pin Work View |
| H | UNVERIFIED · observe-only · paid PARKED · no Ads | **PASS** · EV-W3-001 · observe CTA only |
| I | Esc → Operations Console | **PASS** · focus Enter Virtual HQ |
| J | Desktop / mobile / keyboard | **PASS** · mobile Navigate HQ + Commercial floor · Esc |
| K | Five tabs unchanged | **PASS** · Start · Marketing · Analityka · Agenci · Ustawienia |

---

## 2. Full Marketing status consistency table

**Canonical:** `UNVERIFIED — campaign state not verified` · **EV-W3-001**  
**Explanation:** Campaign SoT requires MKT / Ads Manager verification and is outside current Virtual HQ scope.

| Surface | Status text | Evidence | Consistent |
|---------|-------------|----------|------------|
| VHQ floor card (P1) | `[UNVERIFIED]` | badge | **YES** |
| Marketing Work View | `UNVERIFIED — campaign state not verified` | EV-W3-001 + explanation | **YES** |
| Room panel / VHQ_ROOMS | `[UNVERIFIED]` | EV-W3-001 · SoT outside VHQ | **YES** |
| Department Pulse | `[UNVERIFIED]` | EV-W3-001 | **YES** |
| System Map | `UNVERIFIED — campaign state not verified` · `data-campus-state=UNVERIFIED` | EV-W3-001 | **YES** |
| Settings map list | `P1 Marketing UNVERIFIED — campaign state not verified (EV-W3-001)` | EV-W3-001 | **YES** |
| Truth Cards / Console appendix | `UNVERIFIED — campaign state not verified · EV-W3-001` | EV-W3-001 | **YES** |

**Removed contradictions:** all `NO ACTIVE CAMPAIGN` / `NO_ACTIVE_CAMPAIGN` / `is-no-campaign` from `commander-ui/**` (0 matches after fix).  
**Not done:** Ads Manager inspection · no fake campaign evidence invented.

---

## 3. Screenshots

Saved under `docs/handoffs/evidence-vhq-w3-dogfood/` (local evidence · **do not auto-commit** unless Founder GO):

| Shot | File |
|------|------|
| Sales Work View | `w3-dogfood-sales.png` |
| Wizard Work View | `w3-dogfood-wizard.png` |
| Marketing Work View | `w3-dogfood-marketing.png` |
| Mobile Marketing / Commercial | `w3-dogfood-mobile-marketing.png` · `w3-dogfood-mobile-commercial-floor.png` |
| System Map | `w3-dogfood-map-truth.png` |
| Department Pulse | `w3-dogfood-pulse.png` |

---

## 4. DoD checklist

| DoD | Status |
|-----|--------|
| Sales Work View usable (queue path, no clone) | **PASS** |
| Wizard LIVE hop + honest KPI | **PASS** |
| Marketing UNVERIFIED/PARKED honest pin · observe only | **PASS** |
| No Ads execute · no fake campaign LIVE | **PASS** |
| W2 MC invariants preserved | **PASS** |
| MKT dirty untouched | **PASS** |
| W4 not activated | **PASS** |
| No commit / deploy | **PASS** |

---

## 5. Exact changed files (W3 + truth)

```text
commander-ui/app.js
commander-ui/index.html
commander-ui/styles.css
todo.json
docs/handoffs/2026-07-27-VF-VHQ-W3-ROOMS-COMMERCIAL-PRECLOSE.md
docs/handoffs/2026-07-27-VF-VHQ-W3-FOUNDER-DOGFOOD-TRUTH.md
docs/handoffs/evidence-vhq-w3-dogfood/*   (optional evidence)
```

**Exclude forever from this gate:** `docs/ops/marketing/**`, MKT handoffs, Campus deploy handoffs.

---

## 6. git diff

```text
commander-ui/app.js
commander-ui/index.html
commander-ui/styles.css
todo.json
```

W3 runtime/governance (approx): `4 files changed, 279 insertions(+), 40 deletions(-)` on those paths.  
(MKT dirty files remain modified in working tree — untouched by this session.)

---

## 7. Recommendation

**READY FOR FOUNDER CLOSE**

Next HITL (separate GOs):
1. `CLOSE GO VF-VHQ-W3-ROOMS-COMMERCIAL`
2. `COMMIT GO` (runtime + docs; exclude MKT/evidence unless asked)
3. Optional `DEPLOY GO` tip with `vhq-w03b`
4. W4 stays parked until explicit GO
