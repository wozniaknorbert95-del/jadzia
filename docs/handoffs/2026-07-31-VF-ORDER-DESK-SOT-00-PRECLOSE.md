---
status: "[PRECLOSE · ready_for_human ACCEPT]"
gate: "VF-ORDER-DESK-SOT-00"
updated: "2026-07-31"
runtime_changes_allowed: false
sot: "docs/ops/ORDER-DESK-SOT-v0.md"
verdict: "DISCOVERY DRAFTED · awaiting Founder ACCEPT D1–D5"
prod_baseline: "https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w67a"
---

# PRECLOSE — VF-ORDER-DESK-SOT-00

## Tip-check (session start)

| Check | Result |
|-------|--------|
| Local HEAD | `9e91dc6` |
| Prod commander `?v=vhq-w67a` | HTTP **200** |
| `#vhq-floors` | absent |
| `P3 Sterowanie` | absent |
| EV-W2-010 + Firm signals | present |
| `/health` | **ok** |
| Seal | `FINISHED_PARTIAL_LOOP` preserved |

## DoD discovery

| ID | Deliverable | Result |
|----|-------------|--------|
| D1 | Lifecycle state machine | **DRAFTED** in SoT v0 |
| D2 | Field dictionary + authority split | **DRAFTED** |
| D3 | Exception / disposition matrix L1 | **DRAFTED** |
| D4 | Minimal read-only Work View contract | **DRAFTED** |
| D5 | EV-W2-010 unpark checklist U1–U8 | **DRAFTED** |
| Runtime / Order LIVE / Mollie | — | **NOT built** (correct) |

## Founder action (20–30 min)

Open: `docs/ops/ORDER-DESK-SOT-v0.md` → decision block D1–D5.

Reply: **`ACCEPT VF-ORDER-DESK-SOT-00`** or **`EDIT:`** + notes.

On ACCEPT → next gate proposal: **`VF-ORDER-DESK-WV-00`** (thin read-only Work View).  
S7 stays `blocked_sot` until D5 unpark evidence.

## Parallel HITL (not this gate)

COM-AI disclosure: `docs/ops/marketing/COM-AI-50-READY-PACK.md` — Founder ACCEPT/EDIT. Organic ≥2026-08-02. Ads freeze → 2026-08-06.

## STOP

Fake S7 · Order LIVE · Mollie · Ads · reopen FINAL nav · stage dirty `MKT/` · deploy bez GO
