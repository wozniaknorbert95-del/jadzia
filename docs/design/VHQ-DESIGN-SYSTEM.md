---
status: "[ACTIVE]"
title: "Virtual HQ — Design System (VF-VHQ-DESIGN-00)"
gate: "VF-VHQ-DESIGN-00"
updated: "2026-07-27"
owner: "Norbert Wozniak (Dowódca)"
architecture: "docs/ops/FLEXGRAFIK-VIRTUAL-HQ-ARCHITECTURE.md"
runtime_changes_allowed: false
3d: "HARD-PARKED"
---

# Virtual HQ — Design System

## 1. Concept

**FlexGrafik Virtual HQ** is a professional **2D / isometric** experience layer above Commander.  
The Founder enters a company building, sees honest operational state, visits departments, inspects work, and approves high-risk actions — **without guessing**.

| Layer | Role |
|-------|------|
| Commander (5 tabs) | Control + data foundation — **kept** |
| Campus W1–W3 | Truth map + evidence + Truth Cards — **kept** |
| Virtual HQ | Spatial World + Command + Work views — **this design** |
| 3D | **HARD-PARKED** (`VF-VHQ-3D-PARKED`) |

Inspiration (Talk&Buy store): spatial discoverability only — **no** code, assets, branding, or UI clone.

---

## 2. Visual language (2D / isometric)

### Principles
1. **Command first** — open HQ → Mission Control Command View (not empty map).
2. **Teleport always** — no forced walking; floor jump + search + command palette.
3. **Status ≠ colour alone** — every status has **icon + text label**.
4. **Parked ≠ broken** — locked/dimmed intentional sheet with why + dependency + phase.
5. **Work over décor** — no avatars, no gaming XP, no fake busy agents.
6. **Evidence everywhere** — status chip pairs with `EvidenceChip` + `LastVerified`.
7. **Responsive split** — desktop: World optional; mobile: priorities/approvals, not mini-building.
8. **No 6th Commander tab** — HQ shell overlays / embeds / deep-links existing surfaces.

### Layout tokens (design intent — not CSS yet)

| Token | Intent |
|-------|--------|
| `--vhq-bg` | deep neutral work surface (not game skybox) |
| `--vhq-floor-p3` … `--vhq-floor-mag` | subtle floor tint bands |
| `--vhq-live` | status LIVE (pair with ✓ icon) |
| `--vhq-partial` | PARTIAL (◐) |
| `--vhq-unverified` | UNVERIFIED (?) |
| `--vhq-parked` | PARKED (lock) |
| `--vhq-planned` | PLANNED (dashed) |
| `--vhq-degraded` | DEGRADED (⚠) |
| `--vhq-focus` | Mission Control focal ring |
| Type | UI PL; business labels may be NL where Commander already is |

### Isometric rules (MVP)
- Floors as stacked bands or slight iso slabs — **readable labels mandatory**.
- Rooms = selectable zones with `RoomStatusBadge` + short label.
- Mission Control = **largest / centered** focal on P3.
- Depth cues light; never hide status text.

---

## 3. Status model (honest)

| Status | Icon (text) | Meaning | Interaction |
|--------|-------------|---------|-------------|
| LIVE | `[LIVE]` | Evidence fresh + primary action usable | Enter Work View |
| PARTIAL | `[PARTIAL]` | Works with documented limit | Enter + show limitation banner |
| UNVERIFIED | `[UNVERIFIED]` | Path may exist; claim not proven | Enter read-only / observe |
| PARKED | `[PARKED]` | Conscious stop | Open `ParkedRoomState` sheet only |
| PLANNED | `[PLANNED]` | Architecture only | Open planned sheet |
| DEGRADED | `[DEGRADED]` | LIVE capability + SLO breach | Enter + **cannot hide** incident |

**Never:** invent LIVE desks, fake KPI `0`, fake agents working, colour-only status.

---

## 4. Approval / Command Policy (L0–L4)

| Level | Name | Allowed | Forbidden |
|-------|------|---------|-----------|
| **L0** | Read | Observe status, open SoT read links | Mutate |
| **L1** | Draft / disposition | Ack / Snooze / Close tickets; drafts | External irreversible |
| **L2** | External reversible | Approve agent propose (organic draft, brief) | Spend, Mollie, deploy |
| **L3** | Financial / contractual / deploy | Founder GO class (deploy pack, contract) | Gate D / secrets dump |
| **L4** | Forbidden without explicit GO | Ads spend, Mollie LIVE, Gate D, OS↔jadzia merge | Autonomous execute |

UI must show **risk level on every ApprovalCard**. No autonomous financial actions in Vault.

---

## 5. Three views

| View | Default device | Purpose |
|------|----------------|---------|
| **Command View** | Mobile + desktop entry | Today’s Company Brief · 7 Director questions |
| **World View** | Desktop optional | Floors/rooms orientation · teleport |
| **Work View** | Both | Room queues, evidence, primary actions |

---

## 6. MVP rooms (confirmed)

1. `mission-control` — LIVE  
2. `approval-vault` — PARTIAL (thin MVP)  
3. `ai-agent-health` (**label: Agent Operations**) — PARTIAL / DEGRADED (SSH)  
   - Sub-area: **System Health / AI Health** (probes, INC, OS/VCMS/DA)  
4. `sales-room` — LIVE (queue)  
5. `wizard-quote` — LIVE  

Future/honest pins only where needed: Marketing UNVERIFIED, Finance UNVERIFIED, Order PARKED, Production/Dispatch PARKED, Warehouse PLANNED/PARKED.

Campus **W4** remains **PARKED**. **3D** hard-parked.

---

## 7. Data-driven rooms (no duplicated labels)

All room chrome eventually from **Room Manifest** (see Interaction Spec § Data).  
Hard-coded labels in W1 shell only as bootstrap until manifest file exists — DESIGN requires schema now; runtime in W1+.

### Fields available today (Campus / Commander)

| Field | Available? | Source |
|-------|------------|--------|
| room_id, floor, label | yes (map/Truth Cards) | `index.html` data-* / docs |
| status + evidence | yes (W2/W3) | EV-W2-* / EV-W3-* |
| last_verified_at | yes (Truth Cards) | ISO timestamps |
| sot url | partial | Wizard LIVE; others vary |
| primary_action | yes (Truth Cards) | href / muted none |
| queue tickets | yes (session JWT) | Home queue |
| finance KPI | **no** | insufficient_data |
| order desk | **no** | PARKED |
| campaign state | **no** | EV-W3-001 UNVERIFIED |

### Never inferred by AI
- LIVE status  
- numeric finance / CPA / margin  
- “agent is busy working”  
- Order Desk existence  
- approval outcomes  

---

## 8. Accessibility

- Status: text + icon (not colour alone).  
- Focus order: Brief → Approvals → Risks → Room list.  
- Keyboard: `/` or `Ctrl+K` teleport; `Esc` back to Mission Control; `1–5` MVP rooms (design intent).  
- Touch: min 44px targets; mobile = list, not spatial map.  
- `aria-current` for location; `aria-disabled` for PARKED enter.  

---

## 9. Design dependencies → implementation gates

| Gate | Consumes from DESIGN-00 |
|------|-------------------------|
| W1-SHELL | Blueprint SVG, FloorNavigator, RoomCard, status badges, teleport |
| W2-MISSION-CONTROL | DirectorBrief, Command View wireframe, TruthPanel |
| W3-ROOMS-COMMERCIAL | Sales + Wizard Work Views |
| W4-ROOMS-OPERATIONS | ParkedRoomState patterns |
| W5-OPERATIONS-BUS | OperationsFlowLine, handoff cards, event fields |
| W6-DIRECTOR-APPROVALS | ApprovalCard, L0–L4 policy UI |
| W7-DOGFOOD | Usability scenarios § F |
| 3D | **none — parked** |

---

## 10. STOP (design)

- No 3D assets or perspectives implying shippable 3D  
- No Talk&Buy clone  
- No fake data in wireframe examples (use `insufficient_data` / placeholders marked EXAMPLE)  
- No runtime CSS/JS in this gate  
