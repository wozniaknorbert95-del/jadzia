---
status: "[PRECLOSE]"
title: "VF-VHQ-W3-ROOMS-COMMERCIAL — Commercial Work Views"
updated: "2026-07-27"
gate: "VF-VHQ-W3-ROOMS-COMMERCIAL"
cache: "vhq-w03"
local_url: "http://127.0.0.1:8765/index.html?v=vhq-w03"
prod_tip_unchanged: "db32212 / vhq-w02b"
commit: false
deploy: false
w4_started: false
---

# VF-VHQ-W3-ROOMS-COMMERCIAL — PRECLOSE

**Date:** 2026-07-27  
**Gate:** `VF-VHQ-W3-ROOMS-COMMERCIAL`  
**Decision pending:** Founder dogfood + CLOSE GO  
**Cache (local):** `vhq-w03`  
**Local URL:** `http://127.0.0.1:8765/index.html?v=vhq-w03`  
**Prod tip (unchanged):** `db32212` / `vhq-w02b` — **no deploy this preclose**  
**W4:** not activated (`proposed_next_gate_active: false`)

---

## What shipped (local)

| Surface | Behavior |
|---------|----------|
| Sales Work View | Director Q · handoff Sales→Wizard→Order PARKED · relocated queue + CS · Focus queue · Open Wizard room (in-HQ) · JWT honesty banner |
| Wizard Work View | Director Q · SoT Wizard URL · Open Wizard CTA · KPI `insufficient_data` · Order Desk PARKED child · Mollie L4 STOP copy |
| Marketing honest pin | UNVERIFIED EV-W3-001 · paid PARKED→2026-08-06 · observe → Marketing tab · no Ads controls |
| Cache | `vhq-w03` on CSS/JS/hint |
| Gate | `active_gate=VF-VHQ-W3-ROOMS-COMMERCIAL` · W3 `in_progress` · W4 parked |

---

## Local dogfood checklist

| # | Check | Result |
|---|--------|--------|
| 1 | Cold-open HQ → Mission Control | **PASS** |
| 2 | Sales Work View: queue path + handoff + Open Wizard room | **PASS** |
| 3 | Wizard Work View: Open Wizard URL · insufficient_data · Order PARKED | **PASS** |
| 4 | Marketing pin: UNVERIFIED + paid PARKED · observe only · no Ads | **PASS** |
| 5 | Esc → Operations Console · focus restore · 5 tabs · no 6th | **PASS** |
| 6 | W4 not activated · MKT dirty untouched | **PASS** |
| 7 | W2 MC Brief / SSH DEGRADED / Pulse / Flow preserved | **PASS** |

---

## Files touched (W3-only)

```text
commander-ui/app.js
commander-ui/index.html
commander-ui/styles.css
todo.json
docs/handoffs/2026-07-27-VF-VHQ-W3-ROOMS-COMMERCIAL-PRECLOSE.md
```

**Excluded (do not stage):**

```text
docs/ops/marketing/**
docs/handoffs/2026-07-27-MKT-ASSET-00-PROGRESS.md
docs/handoffs/2026-07-27-DEPLOY-CAMPUS-*
docs/handoffs/2026-07-27-DEPLOY-VHQ-W2-00-CLOSE.md
```

---

## Residuals (honest)

| Residual | Note |
|----------|------|
| Sales disposition needs JWT | Session banner honest; no fake leads |
| Marketing campaign UNVERIFIED | EV-W3-001 — observe only |
| Paid Ads freeze | Until 2026-08-06 |
| Order Desk PARKED | EV-W2-010 — W4 territory |
| SSH DEGRADED | EV-W2-011 — unchanged |

---

## Explicit non-actions

- No commit  
- No deploy  
- No W4 activation  
- No Ads / Mollie / Gate D / new APIs  
- No MKT dirty edit/stage/delete/stash  

---

## Recommended next Founder decision (HITL)

```text
1) Dogfood: http://127.0.0.1:8765/index.html?v=vhq-w03
2) On PASS: CLOSE GO VF-VHQ-W3-ROOMS-COMMERCIAL
3) Then (separate): COMMIT GO → optional DEPLOY GO tip with vhq-w03
4) W4 stays parked until explicit GO VF-VHQ-W4-ROOMS-OPERATIONS
```
