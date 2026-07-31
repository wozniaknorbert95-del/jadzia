---
status: "[SPEC · DISCOVERY]"
title: "VF-ORDER-DESK-SOT-00 — Order Desk Source-of-Truth discovery"
updated: "2026-07-31"
gate: "VF-ORDER-DESK-SOT-00"
program: "docs/ops/FLEXGRAFIK-VIRTUAL-HQ-PROGRAM.md"
blocks: "VF-VHQ-DI-S7-LOOP / EV-W2-010 unpark"
runtime_changes_allowed: false
priority: "P0 next after FINAL seal"
---

# Design: VF-ORDER-DESK-SOT-00 (discovery only)

## 1. Problem

Director Dashboard is sealed (`FINISHED_PARTIAL_LOOP`), but **Deliver** stage stops at honest PARKED.  
INT-002 / `orders` SQLite mirror + `order_created` bus event ≠ operational Order Desk.  
S7 stays `blocked_sot` until a real SoT exists.

## 2. Goal (this gate)

Produce a **Founder-approved SoT contract** that answers:

1. What is the single authoritative record for an order after Wizard/Woo pay?  
2. What lifecycle states exist (quote → paid → brief → production → ship → done/exception)?  
3. Who owns exceptions (L1 triage) and what dispositions exist?  
4. What minimal HQ Work View shows without inventing KPI?  
5. What evidence unparks EV-W2-010?

**Out of scope this gate:** building LIVE desk UI, Mollie LIVE, Production/Dispatch full spine, Ads, 3D.

## 3. Non-goals / STOP

- Fake S7 PASS / Order LIVE without SoT  
- Treating `#3149` or Mollie test as unlock  
- Mega-build fulfilment factory in one session  
- Editing dirty `MKT/`  

## 4. Inputs already in repo

| Asset | Path / note |
|-------|-------------|
| Orders mirror | `agent/db.py` INT-002 `orders` table + list helpers |
| Bus event | `order_created` on Ops Bus cash spine |
| Parked room | `VHQ_ROOMS["order-desk"]` · EV-W2-010 |
| Scorecard S7 | `docs/ops/VHQ-DECISION-INSTRUMENT-SCORECARD.md` |
| Revenue contract | `docs/contracts/REVENUE-EVENT-CONTRACT-v1.md` (if present) |

## 5. Deliverables (binary)

| ID | Deliverable | Pass |
|----|-------------|------|
| D1 | Order lifecycle state machine (mermaid + table) | Founder accept |
| D2 | SoT field dictionary (order_id, states, owner, evidence ids) | Written |
| D3 | Exception / disposition matrix (L1) | Written |
| D4 | Minimal HQ Work View wire (read-only v1) | Sketch in spec |
| D5 | Unpark checklist for EV-W2-010 | Explicit evidence list |
| D6 | BLAST + CLOSE discovery (no runtime) | tip sync |

## 6. Success = unlock next build gate

Only after D1–D5 accept → propose **`VF-ORDER-DESK-WV-00`** (thin read-only Work View) as separate 1-1-1 gate.
