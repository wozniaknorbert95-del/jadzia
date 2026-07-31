# VF-ORDER-DESK-SOT-00 Implementation Plan (discovery)

> **For agentic workers:** Use superpowers:executing-plans or SDD. Checkboxes track work. **No runtime UI/API in this gate.**

**Goal:** Approve Order Desk SoT contract so S7/EV-W2-010 can later unpark honestly.

**Architecture:** Docs + inventory of existing INT-002/bus only. Zero fake LIVE.

**Tech Stack:** markdown specs, existing `agent/db.py` / ops_bus read-only analysis, mermaid.

## Global Constraints

- `runtime_changes_allowed: false`
- No Mollie LIVE / Ads / 3D / Order LIVE badge
- Preserve FINAL seal `vhq-w67a` / F7 nav — no reopen unless regression
- Do not stage dirty `MKT/`
- Parallel HITL: COM-AI ACCEPT stays human-owned (not this gate’s code)

---

### Task 0: BLAST + tip sync

- [ ] Write BLAST handoff  
- [ ] `todo.active_gate=VF-ORDER-DESK-SOT-00`  
- [ ] Park COM-AI remains parked (human lane)  
- [ ] current-task + lanes tip sync  

### Task 1: Inventory current truth

- [ ] Document INT-002 `orders` columns actually used  
- [ ] Document `order_created` payload + who emits  
- [ ] Gap list vs required lifecycle  

### Task 2: Lifecycle + exceptions draft

- [ ] State machine mermaid  
- [ ] Disposition matrix L1  
- [ ] Owner RACI  

### Task 3: Minimal Work View contract

- [ ] Read-only card fields for HQ  
- [ ] Explicit insufficient_data rules  
- [ ] EV-W2-010 unpark checklist  

### Task 4: Founder review CLOSE

- [ ] PRECLOSE discovery pack  
- [ ] Founder ACCEPT / EDIT  
- [ ] Propose next gate `VF-ORDER-DESK-WV-00` only after ACCEPT  

---

## Session timebox (agency)

| Block | Duration | Owner |
|-------|----------|-------|
| Inventory | 45–60 min | Agent |
| Lifecycle draft | 60–90 min | Agent |
| Founder review | 20–30 min | Dowódca |
| CLOSE / next gate | 20 min | Agent |

**DoD session:** D1–D5 drafted; Founder decision recorded; no deploy required.
