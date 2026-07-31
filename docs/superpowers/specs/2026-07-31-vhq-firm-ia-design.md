---
status: "[SPEC]"
title: "VF-VHQ-FIRM-IA-00 — Firm map IA + single shell"
updated: "2026-07-31"
gate: "VF-VHQ-FIRM-IA-00"
program: "docs/ops/FLEXGRAFIK-VIRTUAL-HQ-PROGRAM.md"
priority_order: "A director core → B firm IA → C Order Desk (out of scope)"
approved_by: "Dowódca (brainstorm 2026-07-31)"
runtime_changes_allowed: true
---

# Design: VF-VHQ-FIRM-IA-00

## 1. Problem

Founder wants Virtual HQ to feel like **the company**, not a status dump or a second app beside Operations Console.

Root causes (code + dogfood):

1. **Dual world (D):** Esc ladder and Close semantics treat **Operations Console** as the parent of HQ (`Esc: room → MC → Console`). Console competes with HQ as “home”.
2. **Map is not a firm (B):** Floor labels (P3 Director / P2 Intelligence / P1 Commercial / P0 Operations) read as org-chart tech zones, not a business value chain.
3. **PARKED chaos:** Honest badges without **role + unlock condition** feel like broken company, not intentional roadmap.

Decision Instrument (A: NBA, money/risk, Vault, Decide-now) is **already DONE** — do not rebuild.

Order Desk / cash loop (C) is a **separate project** (`blocked_sot` EV-W2-010).

## 2. Goal

After this gate, Founder cold-opens VHQ and experiences:

- **One home:** HQ / Mission Control  
- **One company story:** Demand → Sell → Deliver → Direct always visible  
- **Console = tools** (JWT / tech / legacy), not exit from the firm  
- **Honest PARKED** with role in the chain  

## 3. Non-goals / STOP

- Order Desk LIVE / S7 fake PASS / inventing fulfilment SoT  
- 3D unpark · Ads · Mollie · Gate D  
- 6th Commander tab  
- New backend APIs / Ops Bus catalog expansion  
- Mass room migration across `P0–P3` IDs in v1  
- Reopening DI scorecard gates S3–S6/S8  

## 4. Architecture

### 4.1 Two axes (keep both)

| Axis | Role | Change in this gate |
|------|------|---------------------|
| `floor` `P0–P3` | Existing shell filter / code SoT | **Keep IDs**; relabel band titles only |
| `firmStage` | Business value chain | **New field** on each room in `VHQ_ROOMS` |

`firmStage` enum:

| Value | UI label (PL primary for Dowódca chrome; EN ok in code comments) | Rooms (current) |
|-------|-------------------------------------------------------------------|-----------------|
| `demand` | Popyt | `marketing-studio` (+ future reception) |
| `sell` | Sprzedaż | `sales-room`, `wizard-quote` |
| `deliver` | Realizacja | `order-desk`, production, dispatch (PARKED) |
| `direct` | Sterowanie | `mission-control`, `approval-vault`, `ai-agent-health`, boardroom, finance pin |

### 4.2 Firm Chain strip (always on)

Above floor tabs / world map: four-stage strip.

- Always visible (not hidden when floor filter changes)  
- Active stage = stage of focused room or selected floor’s dominant stage  
- Click stage → filter/highlight rooms in that stage (does not destroy floor filter; define: stage click sets highlight + scrolls band; floor tabs remain)  

### 4.3 Shell primacy (D) — highest ROI

Current (broken mental model):

```text
Esc: room → Mission Control → Operations Console
Close → Operations Console
```

Target:

```text
Esc: room → Mission Control → stay in HQ (no Console)
Console entry: explicit CTA only — label "Tools / Sign in" (not "Close")
Return to HQ: primary path from Console
Legacy shell: deep link / flag only
```

Concrete UI contract:

| Control | Today | Target |
|---------|-------|--------|
| `#vhq-to-console` | “Operations Console” | “Tools / Sign in” (or PL equivalent consistent with UI language rules) |
| `#vhq-close` | aria “Operations Console” | Must not imply Console is HQ parent; prefer dismiss-to-MC or hide if redundant |
| `.vhq-shell__hint` | Esc … → Operations Console | Esc … → Mission Control (HQ) |
| Cold open | HQ/MC | unchanged |

Eyebrow copy: drop engineer-speak “Commander = engine” as hero; prefer firm framing (e.g. Virtual HQ · FlexGrafik) without lying about LIVE rooms.

### 4.4 PARKED honesty upgrade

For `deliver` (and other PARKED) rooms, each card/modal MUST show:

1. **Role in firm** (one line)  
2. **Status** + evidence ID  
3. **Unlock condition** (e.g. “Order Desk SoT + unpark EV-W2-010”) — not a fake CTA that invents a desk  

No new KPI numbers.

### 4.5 Components (implementation units)

| Unit | Responsibility | Primary files |
|------|----------------|---------------|
| Shell primacy | Esc, CTA labels, hints, Close semantics | `commander-ui/app.js`, `commander-ui/index.html` |
| `firmStage` data | Field on `VHQ_ROOMS` | `commander-ui/app.js` |
| Firm Chain strip | Always-on 4-stage UI | `index.html`, `styles.css`, `app.js` |
| Floor band relabel | P* titles → firm-aligned names | `index.html` (+ JS if dynamic) |
| Room role / unlock copy | Manifest strings | `VHQ_ROOMS` |
| Cache bump | `?v=` + SW | `index.html`, `sw.js` |
| Docs tip sync | todo / PROGRAM / lanes appendix | `todo.json`, ops docs |

No new Python routes required.

## 5. Work packages (order inside gate)

1. **WP-A Shell primacy (D)** — Esc + Console demotion + copy  
2. **WP-B Firm IA (B)** — `firmStage` + strip + PARKED role/unlock + band relabel  
3. **WP-C Regression** — DI surfaces + EV-W2-010 + local dogfood; deploy only with GO  

Each WP: implement → local verify → commit. Deploy once after WP-C with Founder GO.

## 6. Testing / dogfood

### Local

- [ ] Cold open → HQ › Mission Control  
- [ ] Esc from room → MC; second Esc does **not** open Console  
- [ ] Tools/Sign in opens Console; Return to HQ works  
- [ ] Firm Chain strip visible on all floors  
- [ ] Order Desk shows PARKED + role + unlock; no LIVE KPI  
- [ ] NBA / money-risk / Vault still present on MC  

### Prod (after GO DEPLOY)

- [ ] Same checklist on `?v=<new cache>`  
- [ ] Founder can narrate Demand→Sell→Deliver→Direct in ≤30s  
- [ ] Q3/Q6 DI regression still readable  

### Automated

- Prefer existing UI/pytest markers if present; add minimal assertions for Esc/Console parent only if test harness already covers shell. No large new framework.

## 7. Risks

| Risk | Mitigation |
|------|------------|
| Esc change breaks muscle memory of operators who used Console-as-parent | Explicit Tools CTA; dogfood; hint update |
| firmStage vs floor confusion | Document both axes; strip = firm; tabs = floor zones |
| Scope creep into Order Desk | Hard STOP in agent_rule / BLAST |
| Copy language (NL vs PL) | Internal chrome may stay PL for Dowódca; customer-facing elsewhere unchanged |

## 8. Success metrics

- Dual-home complaint resolved (Console ≠ parent)  
- Founder describes map as company chain without prompting  
- Zero fake Order LIVE  
- DI scorecard dimensions S3–S6+S8 remain 5 (regression)  

## 9. Out of scope → next programs

| Later | Gate / note |
|-------|-------------|
| Order Desk SoT + S7 | Separate Founder GO |
| Growth / COM-AI / Ads | After freeze / compliance |
| True 3D | `VF-VHQ-3D-PARKED` |

## 10. Open decisions (locked)

| Decision | Lock |
|----------|------|
| Priority | A maintain → B IA → C later |
| Approach | Firm IA + single shell in one gate, WP-A then WP-B |
| Floor IDs | Keep P0–P3 |
| APIs | None new |
