---
status: "[ACTIVE]"
title: "Virtual HQ — Interaction Spec (VF-VHQ-DESIGN-00)"
gate: "VF-VHQ-DESIGN-00"
updated: "2026-07-27"
runtime_changes_allowed: false
---

# Virtual HQ — Interaction Spec

## 1. Global behaviours

| Trigger | Result |
|---------|--------|
| Open HQ | **Command View / Mission Control** (never empty World) |
| `Esc` / Back | Mission Control Command View |
| Teleport / `⌘K` / `/` | Command palette → room/floor |
| Select PARKED room | `ParkedRoomState` sheet — no fake Work View |
| Select PLANNED room | Planned sheet — purpose + phase only |
| Mobile open | Mobile Director View (priorities + approvals) |

**Forbidden:** forced walking, avatar movement, hiding DEGRADED incidents, inventing queue rows.

---

## 2. MVP room interaction matrices

### 2.1 mission-control

| Field | Spec |
|-------|------|
| entry trigger | HQ open · teleport · breadcrumb |
| default state | Command View with DirectorBrief |
| Director question | What needs my decision today? |
| primary action | Confirm / snooze / close priorities (L1) |
| secondary action | Open Vault · Agent Operations · World · Sales |
| SoT link | Commander Home `?v=campus-w03` |
| displayed evidence | EV-W2-001 + tip + health strip |
| status behavior | LIVE; show DEGRADED child incidents |
| empty state | No CRITICAL/ACTION — honest empty |
| PARKED state | N/A |
| escalation | SSH → Agent Operations; approvals → Vault |
| exit | stays HQ shell; optional Commander tabs |
| keyboard | `1` focus MC; `A` vault; `H` health |
| mobile | Brief-first list |

### 2.2 approval-vault

| Field | Spec |
|-------|------|
| entry | Brief “needs decision” · teleport · MC drawer |
| default | List of pending ApprovalCards (or empty) |
| question | What waits for my stamp? |
| primary | Approve / Reject / Request changes (per level) |
| secondary | Open source room · view audit |
| SoT | Audyt / pending_approval / handoffs |
| evidence | proposal evidence_id + risk L0–L4 |
| status | PARTIAL until session chain verified |
| empty | NoDataState — no invented approvals |
| unavailable | If unauthenticated → prompt login (L0) |
| escalation | L3/L4 → explicit Founder GO gate UI |
| exit | Esc → MC (remaining items still on Brief) |
| keyboard | `A` open; `Y`/`N` design intents for approve/reject |
| mobile | Full-width cards; no side-by-side |

**Rule:** approve writes audit; no silent money moves.

### 2.3 ai-agent-health (label: **Agent Operations**)

**Sub-area:** System Health / AI Health (worker/SSH, DA, OS, VCMS probes).

| Field | Spec |
|-------|------|
| entry | Brief risk · DEGRADED chip · teleport |
| default | AgentHealthCards grid (System Health sub-area) |
| question | Which agent failed or waits? |
| primary | Open incident / health SoT |
| secondary | Hop OS / VCMS / DA health |
| SoT | `/worker/health` · DA health · OS/VCMS URLs |
| evidence | EV-W2-006 · EV-W2-011 · INC-SSH-RECOVERY-00 |
| status | PARTIAL + SSH DEGRADED visible |
| empty | Only if all probes LIVE (rare) |
| PARKED | N/A |
| escalation | INC checklist · cannot hide SSH card |
| exit | Back to MC — Brief still shows DEGRADED |
| keyboard | `H` |
| mobile | Stacked cards |

### 2.4 sales-room

| Field | Spec |
|-------|------|
| entry | Dept health · teleport · Brief priority |
| default | Real lead/sales queue |
| question | Which lead needs a human push now? |
| primary | Disposition Ack/Snooze/Close (L1) |
| secondary | Open Wizard room / Wizard URL |
| SoT | Commander queue · REV-DEMAND |
| evidence | ticket ids; no fake counts |
| status | LIVE when queue API session OK |
| empty | Honest empty queue |
| PARKED | N/A |
| escalation | SLA breach → MC Brief |
| exit | Esc → MC |
| keyboard | `2` |
| mobile | Queue list |

### 2.5 wizard-quote

| Field | Spec |
|-------|------|
| entry | Sales CTA · dept health · teleport |
| default | LIVE panel + Open Wizard |
| question | Is the cash machine reachable? |
| primary | Open Wizard SoT (external) |
| secondary | View Ops Bus handoff to Order (PARKED sheet) |
| SoT | `https://zzpackage.flexgrafik.nl/wizard/` |
| evidence | EV-W2-005 · last_verified |
| status | LIVE |
| empty | N/A (room state, not list) |
| KPI | insufficient_data unless fresh snapshot — **no fake %** |
| PARKED child | Order Desk handoff sheet |
| escalation | Mollie → L4 STOP copy |
| exit | Esc → MC or Sales |
| keyboard | `3` |
| mobile | Big Open Wizard button |

---

## 3. Named Director journeys

### J1 — Open HQ
1. Auth (existing Commander JWT if needed)  
2. Land **Mission Control Command View**  
3. See Brief: decisions · priorities · health · flow break  
**Success:** ≤2 interactions to see “what needs decision”.  

### J2 — Approval
1. Brief → pending item  
2. Open Approval Vault  
3. Read evidence / impact / owner / Lx  
4. Approve | Reject | Request changes  
5. Audit consequence visible  
**Success:** decision recorded; no autonomous finance.  

### J3 — SSH degraded
1. Brief shows `[DEGRADED]` SSH  
2. Open Agent Operations (System Health sub-area)  
3. See INC summary · owner · next action  
4. Cannot dismiss without acknowledge path  
**Success:** incident still on Brief after exit.  

### J4 — Sales issue
1. Brief or dept health → Sales  
2. Real queue OR empty  
3. Optional Wizard  
4. No fake CRM  
**Success:** next action is disposition or Wizard open.  

### J5 — Order Desk attempt
1. World / flow / teleport → Order Desk  
2. `ParkedRoomState`: “Order operational desk is not implemented.”  
3. Why · dependency · future phase (W4 ops)  
4. Back to MC  
**Success:** no LIVE desk implied.  

---

## 4. Room manifest schema (proposal)

```yaml
# docs/ops/vhq/rooms/<room_id>.yaml  (implement from W1+; DESIGN schema only)
room_id: wizard-quote
floor: P1
label: Wizard / Quote Room
purpose: "Cash path — ZZP branding configurator (min EUR 199)"
director_question: "Is the cash machine reachable and healthy?"
status: LIVE
status_evidence: EV-W2-005
last_verified_at: "2026-07-27T14:22:45Z"
owner_role: Sales/Ops
source_of_truth:
  label: Wizard SPA
  url: https://zzpackage.flexgrafik.nl/wizard/
primary_action:
  label: Open Wizard
  href: https://zzpackage.flexgrafik.nl/wizard/
  approval_level: L0
secondary_actions: []
approval_level_max: L4  # Mollie
input_events: [lead_qualified, wizard_started]
output_events: [quote_ready, order_created]
limitations:
  - "Purchase / Mollie LIVE = separate Founder GO"
  - "Order Desk handoff PARKED"
mvp_phase: now
visual:
  metaphor: configurator showroom
  focal: false
```

### Field availability

| Field | Now | Unverified | Future Bus | Never AI-infer |
|-------|-----|------------|------------|----------------|
| room_id/floor/label | ✓ Campus | | | |
| status/evidence/last_verified | ✓ W2/W3 | freshness windows | | **status** |
| sot url | ✓ for Wizard/MC | Knowledge/Finance | | |
| primary_action | ✓ Truth Cards | | | |
| queue payload | ✓ JWT | | | invent rows |
| input/output_events | design only | | **W5** | |
| finance numbers | | ✓ | analytics freshness | **always** |
| order desk live | | | SoT+W4 | **existence** |

---

## 5. Command Policy (UI binding)

| Level | UI affordance | Example |
|-------|---------------|---------|
| L0 | links, open SoT | Open Wizard |
| L1 | disposition buttons | Ack ticket |
| L2 | Approve propose | Organic draft |
| L3 | GO confirm modal + audit | Deploy pack |
| L4 | Hard STOP panel | Ads / Mollie / Gate D |

---

## 6. Operations Bus (interaction)

Visual: `OperationsFlowLine` on Command View.

MVP visible spine:
`Sales [LIVE] → Wizard [LIVE] → Order [PARKED]`

| Handoff | Trigger | Approval | Failure |
|---------|---------|----------|---------|
| Sales → Wizard | disposition / CTA | L0/L1 | requeue |
| Wizard → Order | order_created | L1 | **break visible** PARKED |
| * → Vault | approval_needed | L2–L4 | reject |
| * → Agent Operations | agent_failed | L0 | INC |

No agent chat as workflow.

---

## 7. Usability scenarios (validation)

### S1 — What needs my decision now?
- Path: Open HQ → Brief “Needs decision”  
- Max interactions: **2**  
- Success: see pending Lx items or honest empty  
- Failure: buried under World map / décor  
- Evidence before build: wireframe Command View review  

### S2 — Why is the company at risk?
- Path: Brief → Risks / Agent health / Ops flow break  
- Max: **3**  
- Success: SSH DEGRADED + Order PARKED break visible with evidence  
- Failure: risks only colour dots  
- Evidence: EV-W2-011 listed  

### S3 — Where is Sales and next action?
- Path: Dept health or Go-to-room → Sales → disposition or Wizard  
- Max: **3**  
- Success: real queue or empty + Wizard path  
- Failure: fake CRM funnel  
- Evidence: REV-DEMAND / queue  

### S4 — Can I trust this Finance number?
- Path: World/Brief → Finance pin → UNVERIFIED sheet  
- Max: **2**  
- Success: no number; insufficient_data / EV-W2-008  
- Failure: any invented revenue  
- Evidence: EV-W2-008  

### S5 — Why can’t I use Order Desk?
- Path: Flow break or teleport Order → Parked sheet  
- Max: **2**  
- Success: exact “not implemented” + dependency  
- Failure: LIVE desk chrome  
- Evidence: EV-W2-010  

---

## 8. Non-MVP room behaviour (summary)

| Room | On enter |
|------|----------|
| Marketing | UNVERIFIED observe / Marketing tab deep-link; no Ads |
| Finance | UNVERIFIED sheet → Analityka optional |
| Order/Production/Dispatch | PARKED sheets |
| Reception/CS/Design/Preflight/Warehouse/Partner | PLANNED sheets |
| Supplier | PARKED procurement |
| Boardroom/Knowledge/Compliance/Lab/VCMS-OS | PARTIAL/UNVERIFIED pins — later Work Views |

---

## 9. Implementation notes for W1+

- W1: shell + teleport + status chips + parked sheets + blueprint fidelity  
- W2: Command View Brief bound to real queue/health  
- Do **not** activate W1 in this DESIGN session  
