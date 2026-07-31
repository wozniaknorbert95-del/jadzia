---
status: "[REPORT]"
title: "VF-VHQ-W5 — SoT consistency report (have vs 100%)"
updated: "2026-07-31"
gate: "VF-VHQ-W5-OPERATIONS-BUS"
prod_tip: "67700ff"
cache: "vhq-w50a"
---

# W5 SoT consistency — co mamy vs 100%

**Scope SoT:** Program + Architecture (§8 Bus / §10 BusEvent) + BLAST DoD + `todo.json` tip + prod runtime.  
**Prod tip:** `67700ff` · cache `vhq-w50a` · schema `ops_bus_events` LIVE.

---

## A) Mamy (PASS — spójne z W5 gate)

| # | SoT claim | Runtime / docs | Status |
|---|-----------|----------------|--------|
| 1 | Cash spine typed: `lead_qualified` → `wizard_started` → `order_created` | emit hooks + API + UI trail | **HAVE** |
| 2 | No free-form agent chat as workflow | bus cards typed only | **HAVE** |
| 3 | Audit via `append_audit` on emit | emit path | **HAVE** |
| 4 | L2 pending; L3/L4 STOP + approve forbidden | API + tests | **HAVE** |
| 5 | Kill-switch `ops_bus_enabled` | flags + empty GET | **HAVE** |
| 6 | Order Desk PARKED EV-W2-010 | prod UI + local dogfood | **HAVE** |
| 7 | JWT required for bus list/ingest | prod API smoke | **HAVE** |
| 8 | Cache bust `vhq-w50a` | index/sw prod | **HAVE** |
| 9 | pytest EV-W5 path | 9/9 ops_bus + smoke | **HAVE** |
| 10 | Deploy tip = git tip = docs tip | `67700ff` | **HAVE** (after this tip-sync) |
| 11 | Worker SSH honesty | `ssh_connection=ok` | **HAVE** |

---

## B) Luki do 100% spójności SoT (docs / residual / next gates)

| # | Gap | Impact | Fix class | Owner |
|---|-----|--------|-----------|-------|
| G1 | `FLEXGRAFIK-VIRTUAL-HQ-PROGRAM.md` §6 still says Ops Bus runtime „Out of MVP / implement W5” | Program SoT stale vs LIVE | **docs tip-sync this commit** | agent |
| G2 | `FLEXGRAFIK-VIRTUAL-HQ-ARCHITECTURE.md` §10 comment „not runtime now” for BusEvent | Architecture stale | **docs tip-sync this commit** | agent |
| G3 | Full catalog §8 beyond cash spine (`quote_ready`, `design_brief_ready`, `preflight_pass`, …) | intentional W5 out-of-scope | **W6+ / future gates** | parked |
| G4 | Prod UI bus cards require JWT session — cold-open shows honesty shells without trail | expected; Founder JWT session for full UI trail | **human dogfood JWT on prod** (optional polish) | Dowódca |
| G5 | `order_created` proven in pytest; no new WC order forced on prod for dogfood | correct STOP (no Order LIVE / no fake WC) | **accept residual** until next real WC insert | — |
| G6 | Uncommitted local MKT dirt + old handoffs outside W5 | risk of dirty commit | **keep unstaged** | operator hygiene |
| G7 | W6 Approval Vault UX not started | Architecture L2–L4 UX incomplete | **separate GO W6** | parked |
| G8 | Program dependency row still mentions old Commander tip / INC-SSH DEGRADED narrative | tip/SSH outdated in §8 deps | **docs polish** (this or next tip-sync) | agent |
| G9 | Scorecard / AGENTS campus tip may still say `vhq-w40c` in places | tip drift | grep+update remaining tip refs | agent |

---

## C) Definition — „100% SoT spójność” for W5

**W5 gate 100%** = A1–A11 + G1–G2 + tip refs (G8/G9 docs) closed.  
**Program-wide 100%** (full §8 catalog + Order LIVE + W6) ≠ W5 — requires later gates + separate GOs.

### After this tip-sync

| Layer | Target |
|-------|--------|
| Runtime | tip `67700ff` · cache `vhq-w50a` · `ops_bus_events` |
| Gate status | W5 `completed` · deploy stamped |
| Docs | Program/Architecture acknowledge cash-spine bus LIVE |
| Residuals accepted | G3–G7 (catalog / JWT UI / order_created live WC / MKT dirt / W6) |

---

## D) Recommended next (no-ask)

1. Tip-sync docs (G1/G2/G8/G9) + push + VPS docs pull  
2. Optional: Founder JWT prod dogfood for bus cards on Wizard  
3. Park W6 until explicit GO  
4. Do **not** chase full §8 catalog under W5  

REPORT_VERDICT: **W5 runtime LIVE · docs tip-sync closes SoT drift · catalog residuals = later gates**
