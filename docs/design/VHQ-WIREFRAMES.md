---
status: "[ACTIVE]"
title: "Virtual HQ — Wireframes (VF-VHQ-DESIGN-00)"
gate: "VF-VHQ-DESIGN-00"
updated: "2026-07-27"
fidelity: "low/medium — ASCII + structure; SVG blueprint separate"
runtime_changes_allowed: false
---

# Virtual HQ — Wireframes

Blueprint SVG: [`vhq-mvp-blueprint.svg`](./vhq-mvp-blueprint.svg)  
Design system: [`VHQ-DESIGN-SYSTEM.md`](./VHQ-DESIGN-SYSTEM.md)

Legend: `[LIVE]` `[PARTIAL]` `[UNVERIFIED]` `[PARKED]` `[PLANNED]` `[DEGRADED]` · `EV-*` = evidence id · `—` = insufficient_data

---

## 0. Shell chrome (all desktop views)

```text
┌─ HQShell ─────────────────────────────────────────────────────────────┐
│ FlexGrafik Virtual HQ · tip ref · [Teleport ⌘K] [Search] [?]          │
│ Breadcrumb: HQ › P3 › Mission Control                                 │
│ Floors: [P3●] [P2] [P1] [P0] [MAG]     View: [Command●] [World]       │
├───────────────────────────────────────────────────────────────────────┤
│ …view body…                                                           │
└───────────────────────────────────────────────────────────────────────┘
```

Mobile shell: **no World toggle by default** — Command + “Go to room”.

---

## 1. Director Command View (default entry)

**Purpose:** ≤30s company brief. Lands here on open HQ.

```text
┌─ Command View / Mission Control ──────────────────────────────────────┐
│ TODAY'S COMPANY BRIEF                          last_verified: ISO     │
│                                                                       │
│ ┌ What needs my decision? ──────────────────────────────────────────┐ │
│ │ Approval queue (n)  [PARTIAL] EV-…                                │ │
│ │ • [L2] Calendar draft …  [Open Vault]                             │ │
│ │ • [L3] Deploy pack …     [Open Vault]                             │ │
│ │ empty → “No pending approvals in this window”                     │ │
│ └───────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│ Top 3 priorities (from queue CRITICAL/ACTION — real tickets only)     │
│ 1. … ticket … [Ack] [Snooze] [Open room]                               │
│ 2. …                                                                  │
│ 3. …                                                                  │
│ (if none) NoDataState — do not invent priorities                      │
│                                                                       │
│ ┌ Department health ─────────┐  ┌ Agent health ─────────────────────┐ │
│ │ Sales     [LIVE]     EV-.. │  │ Worker SSH [DEGRADED] EV-W2-011   │ │
│ │ Wizard    [LIVE]     EV-.. │  │ Design Agent [LIVE] EV-W2-006      │ │
│ │ Marketing [UNVERIFIED]     │  │ Agent OS [PARTIAL]                │ │
│ │ Finance   [UNVERIFIED]     │  │ VCMS [PARTIAL]                    │ │
│ │ Orders    [PARKED]         │  │ → Open Agent Operations           │ │
│ └────────────────────────────┘  └───────────────────────────────────┘ │
│                                                                       │
│ Ops flow at risk (OperationsFlowLine — MVP: Sales→Wizard→Order)       │
│ [Sales LIVE] → [Wizard LIVE] → [Order PARKED] ⚠ break visible         │
│                                                                       │
│ Next best action: <one PrimaryAction from highest risk>               │
│ Untrusted / not built: Finance UNVERIFIED · Order PARKED · 3D PARKED  │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 2. World / Building View (desktop)

```text
┌─ World View ──────────────────────────────────────────────────────────┐
│ Teleport list │ Search rooms… │ You are here: P3 Mission Control      │
├───────────────┴───────────────────────────────────────────────────────┤
│                                                                       │
│  P3 DIRECTOR ═══════════════════════════════════════════════════════  │
│   ┌Boardroom┐ ┌████ MISSION CONTROL ████┐ ┌Approval Vault┐ ┌Agent Ops┐│
│   │PARTIAL  │ │ LIVE · focal            │ │ PARTIAL      │ │DEGRADED ││
│   └─────────┘ └─────────────────────────┘ └──────────────┘ └─────────┘│
│                                                                       │
│  P2 INTELLIGENCE ═══════════════════════════════════════════════════  │
│   Finance UNVERIFIED · Compliance PARTIAL · Knowledge UNVERIFIED      │
│   Data&AI PARTIAL · VCMS/OS zone PARTIAL                              │
│                                                                       │
│  P1 COMMERCIAL ═════════════════════════════════════════════════════  │
│   Reception PLANNED · Sales LIVE · Wizard LIVE · Marketing UNVERIFIED │
│   Client Support PLANNED · Design Studio PLANNED                      │
│                                                                       │
│  P0 OPERATIONS ═════════════════════════════════════════════════════  │
│   Order PARKED · Production PARKED · Preflight PLANNED · Dispatch PARK│
│                                                                       │
│  MAG NETWORK ═══════════════════════════════════════════════════════  │
│   Supplier PARKED · Asset Warehouse PLANNED · Partner Net PLANNED     │
│                                                                       │
│ Click room → Work View or Parked/Planned sheet. No walking required.  │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 3. Mission Control Room — Work View

```text
┌─ Work: Mission Control [LIVE] EV-W2-001 · verified ISO ───────────────┐
│ Purpose: company priorities, alerts, approvals, health                │
│ Q: What needs my decision today?                                      │
│                                                                       │
│ Priorities / queue (JWT session)     │ Risk / exceptions              │
│ • CRITICAL …                         │ • SSH DEGRADED → Agent Ops     │
│ • ACTION …                           │ • Order desk PARKED (info)     │
│                                      │                                │
│ Approval drawer (peek)               │ Evidence trail                 │
│ pending n → Open Approval Vault      │ EV-W2-001 · tip · health       │
│                                                                       │
│ Primary: Confirm / snooze / close priorities                          │
│ Secondary: Open World · Open Agent Operations · Open Vault            │
│ SoT: Commander Home                                                   │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 4. Sales Room — Work View

```text
┌─ Work: Sales Room [LIVE] ─────────────────────────────────────────────┐
│ Q: Which lead needs a human push now?                                 │
│                                                                       │
│ Lead / sales queue (real tickets only)                                │
│ • hot_lead … [Ack] [Snooze] [Close] [Open Wizard]                     │
│                                                                       │
│ Handoff strip: Sales → Wizard [LIVE] → Order Desk [PARKED]            │
│                                                                       │
│ Limitations: no invented CRM pipeline; no fake lead counts            │
│ Primary: Disposition queue item                                       │
│ Secondary: Enter Wizard / Quote Room                                  │
│ SoT: Commander queue / REV-DEMAND                                      │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 5. Wizard / Quote Room — Work View

```text
┌─ Work: Wizard / Quote [LIVE] EV-W2-005 ───────────────────────────────┐
│ Q: Is the cash machine reachable and healthy?                         │
│                                                                       │
│ Status: LIVE · Wizard SPA Stap 1–9                                    │
│ SoT: https://zzpackage.flexgrafik.nl/wizard/                          │
│ Primary action: [Open Wizard] (external)                              │
│                                                                       │
│ KPI: wizard_starts → insufficient_data unless fresh GA4 snapshot      │
│ NEVER show fake conversion % / revenue                                │
│                                                                       │
│ Future handoff: → Order Desk [PARKED]                                 │
│ “Order operational desk is not implemented.”                          │
│                                                                       │
│ Limitation: Mollie LIVE / Purchase = L4 separate GO                   │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 6. Approval Vault

```text
┌─ Work: Approval Vault [PARTIAL] EV-W2-009 ────────────────────────────┐
│ Q: What waits for my stamp?                                           │
│                                                                       │
│ ┌ ApprovalCard ─────────────────────────────────────────────────────┐ │
│ │ Title / proposal                                                   │ │
│ │ Risk: L2 · Owner: Marketing · Source room: marketing-studio        │ │
│ │ Evidence: … · Impact: …                                            │ │
│ │ [Approve] [Reject] [Request changes]                               │ │
│ │ Audit: will write evidence + audit event                           │ │
│ └───────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│ Banner: No autonomous financial actions. L3/L4 need explicit GO.      │
│ Empty: NoDataState                                                    │
│ Limitation: chain detail needs authenticated session (PARTIAL)        │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 7. Agent Operations (MVP room)

**Label:** Agent Operations · `room_id`: `ai-agent-health`  
**Sub-area:** System Health / AI Health (probes, INC, DA/OS/VCMS)

```text
┌─ Work: Agent Operations [PARTIAL/DEGRADED] ───────────────────────────┐
│ Q: Which agent failed or waits?                                       │
│                                                                       │
│ ── Sub-area: System Health / AI Health ─────────────────────────────  │
│ ┌ AgentHealthCard: Worker / SSH ────────────────────────────────────┐ │
│ │ [DEGRADED] ssh_connection=error · EV-W2-011 · INC-SSH-RECOVERY-00 │ │
│ │ Owner: Ops/COI · Next: open incident checklist                     │ │
│ │ Incident CANNOT be dismissed without acknowledge path              │ │
│ └───────────────────────────────────────────────────────────────────┘ │
│ ┌ Design Agent ──────┐ ┌ Agent OS ────────┐ ┌ VCMS ─────────────────┐ │
│ │ [LIVE] EV-W2-006   │ │ [PARTIAL] auth   │ │ [PARTIAL] post-auth   │ │
│ │ Open health JSON   │ │ Hop os.…         │ │ Hop cmd.…             │ │
│ └────────────────────┘ └──────────────────┘ └───────────────────────┘ │
│ Primary: Open incident / health SoT                                   │
│ Secondary: Back to Mission Control (incident still listed on Brief)   │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 8. Mobile Director View

**Not a mini building.**

```text
┌─ Mobile HQ ──────────────────┐
│ Company Brief · verified ISO │
│                              │
│ NEEDS DECISION               │
│ • L2 … [Vault]               │
│                              │
│ TOP PRIORITIES               │
│ • … [Ack]                    │
│                              │
│ RISKS                        │
│ • SSH DEGRADED [Agent Ops]   │
│ • Order PARKED [Why?]        │
│                              │
│ Go to room ▾                 │
│  Mission Control             │
│  Approval Vault              │
│  Agent Operations            │
│  Sales                       │
│  Wizard                      │
│  (Parked rooms → sheet)      │
│                              │
│ [Teleport search]            │
└──────────────────────────────┘
```

---

## 9. Parked room sheet (Order Desk example)

```text
┌─ Order Desk [PARKED] EV-W2-010 ───────────────────────────────────────┐
│ Order operational desk is not implemented.                            │
│ Why: no live SoT / operational desk UI                                │
│ Dependency: Order Desk SoT + VF-VHQ-W4-ROOMS-OPERATIONS               │
│ Historical INT-002 #3149 ≠ live desk                                  │
│ [Back to Mission Control]  [View Ops Bus break]                       │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 10. Wireframe → gate mapping

| Wireframe | First implement gate |
|-----------|----------------------|
| Shell + World | W1-SHELL |
| Command View | W2-MISSION-CONTROL |
| MC / Sales / Wizard Work | W2 + W3 |
| Approval Vault | W6 (thin peek in W2) |
| Agent Operations (System Health sub-area) | W2 |
| Mobile | W1–W2 |
| Parked sheets | W1 + W4 |
