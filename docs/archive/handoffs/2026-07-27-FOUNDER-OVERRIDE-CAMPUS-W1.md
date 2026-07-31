---
status: "[ACTIVE]"
title: "Founder priority override — Campus W1 only"
updated: "2026-07-27"
gate: "VF-CAMPUS-W1"
decision: "FOUNDER PRIORITY OVERRIDE"
---

# Handoff — 2026-07-27 (Founder override → Campus)

## Decision (Accountable = Dowódca)

**Founder priority override:** build FlexGrafik Virtual Campus / Mission Control.  
**Marketing `MKT-ASSET-00`:** `parked` (`parked_by_founder`) — **not** completed.  
**No** marketing deliverables, video, Ads, GTM execution, Mollie/Purchase in Campus sessions.

## Control plane (applied)

| Field | Value |
|-------|-------|
| `active_gate` | **`VF-CAMPUS-W1`** (`in_progress`) |
| `MKT-ASSET-00` | `parked` — note: Founder priority override: Campus/Mission Control only. No marketing work. |
| W2 / W3 / W4 | remain `parked` |
| W1 `depends_on` | `VF-CAMPUS-PLAN-00` only (MKT dependency removed by override) |

## Evidence
- Founder message 2026-07-27: `FOUNDER PRIORITY OVERRIDE — CAMPUS ONLY` + explicit GO for `VF-CAMPUS-W1`
- Handoff this file
- `todo.json` gate_machine.founder_override

## Next
1. Agent delivers `VF-CAMPUS-W1 — Implementation Plan` (no UI until `EXECUTE VF-CAMPUS-W1`)
2. Founder replies `EXECUTE VF-CAMPUS-W1`
3. Implement Navigate / System Map metadata only — no deploy, no commit without ask
