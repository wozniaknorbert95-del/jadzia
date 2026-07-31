# VF-VHQ-FINAL-00 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish Director Dashboard: one Firm Chain nav axis, Finish Cards, MVP Work View polish, seal without fake Order Desk.

**Architecture:** Keep `floor` on `VHQ_ROOMS` as data; UI filter solely by `firmStage`. Hide `#vhq-floors`. Cache `vhq-w67a`. Console = Tools. S7 stays parked.

**Tech Stack:** commander-ui (HTML/CSS/JS), pytest string contracts, existing commander/ops_bus APIs.

## Global Constraints

- No Order Desk LIVE / S7 fake PASS / EV-W2-010 invent
- No Ads / Mollie / 3D / Gate D / 6th tab
- No deploy without Founder `GO DEPLOY`
- Do not stage dirty `docs/ops/marketing/MKT/`
- Spec: `docs/superpowers/specs/2026-07-31-vhq-final-dashboard-design.md`
- Supersedes FIRM-IA dual floor tabrow UI

---

### Task 0: W0 Seal SoT

**Files:**
- Create: `docs/superpowers/specs/2026-07-31-vhq-final-dashboard-design.md`
- Create: `docs/superpowers/plans/2026-07-31-vhq-final-dashboard.md`
- Create: `docs/handoffs/2026-07-31-VF-VHQ-FINAL-00-BLAST.md`
- Modify: `todo.json`, `docs/ops/FLEXGRAFIK-VIRTUAL-HQ-PROGRAM.md`, `docs/ops/PROGRAM-LANES-SOT.md`, `docs/ops/marketing/OPERATOR-TODAY.md`, `.cursor/current-task.md`, `docs/ops/VHQ-DECISION-INSTRUMENT-SCORECARD.md` (S2 note)

- [x] Spec + plan + BLAST
- [x] `active_gate=VF-VHQ-FINAL-00`; park COM-AI
- [x] Tip-sync atomowy

### Task 1: W1 Nav One Axis

**Files:**
- Modify: `commander-ui/index.html`, `commander-ui/app.js`, `commander-ui/styles.css`, `commander-ui/sw.js`
- Create: `tests/unit/test_vhq_final_contracts.py`

- [ ] Hide/remove `#vhq-floors` from primary UI
- [ ] Filter map by `firmStage` only; MAG under deliver
- [ ] Breadcrumb stage+room (no P3/MAG chrome)
- [ ] Cache `vhq-w67a`
- [ ] Contract tests F7 green

### Task 2: W2 Finish Cards

**Files:**
- Modify: `commander-ui/app.js` (room shell renderer / Finish Card)

- [ ] Every room shows Finish Card fields when not full Work View
- [ ] Registry honesty for lastVerified
- [ ] Deliver stage banner EV-W2-010

### Task 3: W3 MVP Work Views

**Files:**
- Modify: `commander-ui/app.js` (+ thin HTML/CSS if needed)

- [ ] Agent Ops health/hop strip
- [ ] Finance insufficient_data + Tools CTA
- [ ] Marketing observe-only + Ads freeze copy
- [ ] Vault pending/owner consistency polish

### Task 4: W4 Seal

- [ ] Local dogfood F1–F7
- [ ] PRECLOSE; ready_for_go_deploy (VPS only with GO DEPLOY)
- [ ] tip sync; CLOSE when deploy done or PRECLOSE parked
