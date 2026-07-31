---
status: "[READY-FOR-FOUNDER]"
title: "VF-VHQ-W4 — Founder Dogfood Pack"
updated: "2026-07-31"
gate: "VF-VHQ-W4-ROOMS-OPERATIONS"
cache: "vhq-w40a"
local_url: "http://127.0.0.1:8765/index.html?v=vhq-w40a"
prod_tip_unchanged: "de10e83 / vhq-w32a"
---

# VF-VHQ-W4 — Founder Dogfood Pack

**Gate:** `VF-VHQ-W4-ROOMS-OPERATIONS`  
**Local:** `http://127.0.0.1:8765/index.html?v=vhq-w40a`  
**Agent local dogfood:** PASS (see PRECLOSE)  
**Your job:** confirm honesty + CLOSE GO (or FAIL with notes)

Serve UI:

```text
cd commander-ui
python -m http.server 8765
```

---

## Checklist (mark PASS/FAIL)

| # | Step | Expected | Result |
|---|------|----------|--------|
| 1 | Open local URL | Cache hint `vhq-w40a` | |
| 2 | Cold-open → Mission Control | Command mode; no fake KPI | |
| 3 | Teleport / open **Order Desk** | Work View · **PARKED** · **EV-W2-010** · insufficient_data · no LIVE CTA | |
| 4 | Open **Production Control** | Work View · PARKED · EV-W4-001 · Erka HITL only | |
| 5 | Open **Preflight / Quality** | Work View · PLANNED · EV-W4-002 | |
| 6 | Open **Dispatch / Returns** | Work View · PARKED · EV-W4-003 | |
| 7 | Wizard → Order handoff button | Order Work View PARKED EV-W2-010 | |
| 8 | Console Truth Card Order | EV-W2-010 · desk not implemented | |
| 9 | Ops flow break | Order desk not implemented | |
| 10 | Sales / Wizard / Marketing | Still work; Marketing UNVERIFIED EV-W3-001 | |
| 11 | Esc / Console / legacy `?vhq_shell=legacy` | Primary+legacy still usable | |
| 12 | Tabs | Still 5 · no 6th · no Ads/Mollie | |

---

## CLOSE decision

On all PASS:

```text
CLOSE GO VF-VHQ-W4-ROOMS-OPERATIONS
```

Then (separate sessions / GO):

```text
COMMIT GO   (exclude docs/ops/marketing/**)
DEPLOY GO   (tip + cache vhq-w40a) — Zasada 11
```

**STOP without CLOSE GO:** do not mark gate completed · do not commit · do not deploy · do not start W5.
