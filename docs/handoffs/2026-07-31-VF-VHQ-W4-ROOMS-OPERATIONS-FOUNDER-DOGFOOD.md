---
status: "[READY-FOR-FOUNDER-STAMP]"
title: "VF-VHQ-W4 — LIVE Founder 5-min stamp pack"
updated: "2026-07-31"
gate: "VF-VHQ-W4-ROOMS-OPERATIONS"
cache: "vhq-w40c"
prod_url: "https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w40c"
prod_tip_runtime: "b6d0d36"
prod_tip_docs: "78fa49d+"
w4_closed_deployed: true
founder_stamp: pending
---

# VF-VHQ-W4 — LIVE Founder 5-min stamp

**Gate:** CLOSED + DEPLOYED (tip runtime `b6d0d36` · cache `vhq-w40b`)  
**Prod URL:** https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w40c  
**Your job (≤5 min):** open URL · stamp PASS/FAIL below  
**Agent dogfood:** see `docs/handoffs/2026-07-31-VF-VHQ-W4-LIVE-DOGFOOD.md` (PASS @ vhq-w40b; honesty refresh @ vhq-w40c)  
**SSH:** INC-SSH-RECOVERY-00 CLOSED — `ssh_connection=ok`

---

## Checklist (stamp Result)

| # | Step | Expected | Agent | Founder |
|---|------|----------|-------|---------|
| 1 | Open prod URL | Cache hint `vhq-w40c` | **PASS** (agent @40b; stamp @40c) | |
| 2 | Cold-open → Mission Control | Command mode; no fake KPI | **PASS** | |
| 3 | Open **Order Desk** | Work View · **PARKED** · **EV-W2-010** · insufficient_data · no LIVE CTA | **PASS** | |
| 4 | Open **Production Control** | Work View · PARKED · EV-W4-001 · Erka HITL only | **PASS** | |
| 5 | Open **Preflight / Quality** | Work View · PLANNED · EV-W4-002 | **PASS** | |
| 6 | Open **Dispatch / Returns** | Work View · PARKED · EV-W4-003 | **PASS** | |
| 7 | Wizard → Order handoff | Order Work View PARKED · EV-W2-010 on button | **PASS** | |
| 8 | Console Truth Card Order | EV-W2-010 · desk not implemented | **PASS** | |
| 9 | Ops flow break | EV-W2-010 visible | **PASS** | |
| 10 | Sales / Wizard / Marketing | Marketing UNVERIFIED EV-W3-001 | **PASS** | |
| 11 | Legacy `?vhq_shell=legacy` | Shell usable | **PASS** | |
| 12 | Tabs | Still 5 · no 6th · no Ads/Mollie | **PASS** | |

---

## Founder stamp

```text
FOUNDER STAMP: PASS | FAIL
Date:
Notes:
```

**Not required for INC-SSH start** if agent dogfood = PASS.  
**STOP:** do not start W5 · do not touch MKT · do not fake Order LIVE.
