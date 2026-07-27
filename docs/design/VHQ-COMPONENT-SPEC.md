---
status: "[ACTIVE]"
title: "Virtual HQ — Component Spec (VF-VHQ-DESIGN-00)"
gate: "VF-VHQ-DESIGN-00"
updated: "2026-07-27"
runtime_changes_allowed: false
---

# Virtual HQ — Component Spec

All components are **design contracts** for W1+. No runtime code in DESIGN-00.

Shared rules:
- Status always **icon + text** (never colour alone).  
- Stale evidence → show `LastVerified` + degrade claim to UNVERIFIED/insufficient_data — never invent.  
- Loading → skeleton; no fake rows.  
- a11y: focusable, named, `aria-*` for status/disabled.

---

## HQShell

| | |
|--|--|
| **Purpose** | App chrome: title, view switch, breadcrumb, teleport entry |
| **Props** | `view: command\|world\|work`, `location: {floor, room_id}`, `tipRef?` |
| **States** | default · unauthenticated banner · offline |
| **A11y** | landmark `banner` + `main`; skip link to Brief |
| **Loading** | chrome immediate; body skeleton |
| **Forbidden** | 6th Commander tab; 3D stage; avatar |

---

## FloorNavigator

| | |
|--|--|
| **Purpose** | Jump P3/P2/P1/P0/MAG without walking |
| **Props** | `floors[]`, `currentFloor`, `onSelect` |
| **States** | idle · selected · disabled(floor empty) |
| **A11y** | `tablist` / `tab` |
| **Forbidden** | scroll-jacking; forced path animation |

---

## RoomCard

| | |
|--|--|
| **Purpose** | Selectable room on World / lists |
| **Props** | `room_id`, `label`, `status`, `evidence_id?`, `mvp?`, `focal?` |
| **States** | LIVE/PARTIAL/UNVERIFIED/PARKED/PLANNED/DEGRADED · hover · focus · selected |
| **A11y** | button/link; `aria-current` if here |
| **No-data** | still show label + status |
| **Forbidden** | fake occupancy; LIVE without evidence prop |

---

## RoomStatusBadge

| | |
|--|--|
| **Purpose** | Honest status chip |
| **Props** | `status`, `labelText` (required) |
| **States** | each status enum |
| **A11y** | text node includes status word |
| **Forbidden** | colour-only encoding |

---

## EvidenceChip

| | |
|--|--|
| **Purpose** | Show evidence id (e.g. EV-W2-001) |
| **Props** | `evidence_id`, `href?` |
| **States** | present · missing→hide section not invent |
| **Forbidden** | fabricate EV ids |

---

## LastVerified

| | |
|--|--|
| **Purpose** | ISO timestamp of last verify |
| **Props** | `iso`, `staleAfterHours?` |
| **States** | fresh · stale (visual + copy) · null→`insufficient_data` |
| **Forbidden** | clock-skew hide; fake “just now” |

---

## PrimaryAction

| | |
|--|--|
| **Purpose** | Single primary CTA for room |
| **Props** | `label`, `href\|command_id`, `approval_level`, `disabled?`, `disabledReason?` |
| **States** | enabled · disabled · L3/L4 confirm gated |
| **Forbidden** | multiple competing primaries; L4 without STOP UI |

---

## TruthPanel

| | |
|--|--|
| **Purpose** | Purpose · question · status · SoT · limitations (Campus Truth Card DNA) |
| **Props** | manifest slice |
| **States** | loaded · incomplete fields muted |
| **Forbidden** | KPI numbers without SoT freshness |

---

## ApprovalCard

| | |
|--|--|
| **Purpose** | One approval proposal |
| **Props** | `title`, `risk: L0-L4`, `owner`, `source_room`, `evidence_id`, `impact`, `actions` |
| **States** | pending · approved · rejected · changes_requested |
| **A11y** | group with labelled buttons |
| **Forbidden** | auto-approve; hide risk; financial L3/L4 without GO modal |

---

## RiskCard

| | |
|--|--|
| **Purpose** | Company risk / exception on Brief |
| **Props** | `title`, `status`, `evidence_id`, `cta` |
| **States** | open · acknowledged (still listed if DEGRADED) |
| **Forbidden** | dismiss DEGRADED without path |

---

## AgentHealthCard

| | |
|--|--|
| **Purpose** | One agent/system health |
| **Props** | `name`, `status`, `evidence_id`, `owner`, `next_action`, `sot_href?` |
| **States** | LIVE/PARTIAL/DEGRADED/UNVERIFIED |
| **Forbidden** | animated “working” without task SoT |

---

## ParkedRoomState

| | |
|--|--|
| **Purpose** | Intentional unavailable room sheet |
| **Props** | `room_id`, `headline`, `why`, `dependency`, `phase`, `evidence_id` |
| **States** | parked (only) |
| **Copy example** | “Order operational desk is not implemented.” |
| **Forbidden** | look like error 500; offer fake enter |

---

## NoDataState

| | |
|--|--|
| **Purpose** | Honest empty |
| **Props** | `context`, `hint?` |
| **Forbidden** | placeholder lorem tickets; zeros as fake KPI |

---

## OperationsFlowLine

| | |
|--|--|
| **Purpose** | Cross-dept spine with break visibility |
| **Props** | `nodes: {room_id, status}[]`, `highlightBreak?` |
| **MVP** | Sales → Wizard → Order |
| **Forbidden** | agent chat bubbles as flow |

---

## DepartmentHandoffCard

| | |
|--|--|
| **Purpose** | One typed handoff summary |
| **Props** | `event_type`, `from`, `to`, `approval_level`, `state` |
| **States** | proposed · approved · blocked · parked_dest |
| **Forbidden** | free-text agent dialogue as state |

---

## DirectorBrief

| | |
|--|--|
| **Purpose** | Today’s Company Brief composition |
| **Props** | `priorities[]`, `approvals[]`, `deptHealth[]`, `agentHealth[]`, `flow`, `nextAction`, `untrusted[]`, `last_verified` |
| **States** | loading · ready · partial (some slices insufficient_data) |
| **Forbidden** | invent top-3; hide untrusted section |

---

## CommandPalette / Teleport

| | |
|--|--|
| **Purpose** | Search rooms/floors/actions |
| **Props** | `items[]`, `onSelect` |
| **States** | closed · open · no results |
| **A11y** | combobox / listbox |
| **Forbidden** | only mouse World navigation |

---

## Composition map

```text
HQShell
├─ FloorNavigator
├─ CommandPalette
├─ Command View
│  └─ DirectorBrief
│     ├─ ApprovalCard*
│     ├─ RiskCard*
│     ├─ RoomStatusBadge (dept)
│     ├─ AgentHealthCard*
│     └─ OperationsFlowLine
├─ World View
│  └─ RoomCard*
└─ Work View
   ├─ TruthPanel
   ├─ PrimaryAction
   ├─ EvidenceChip + LastVerified
   ├─ ParkedRoomState | NoDataState
   └─ DepartmentHandoffCard?
```

---

## Forbidden globally

- Talk&Buy assets/branding  
- 3D meshes  
- Fake LIVE / fake people  
- Colour-only status  
- Autonomous L3/L4  
- New Commander primary tab  
