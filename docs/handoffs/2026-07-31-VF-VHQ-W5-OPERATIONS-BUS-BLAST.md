---
status: "[BLAST]"
title: "VF-VHQ-W5-OPERATIONS-BUS — BLAST (typed cash spine)"
updated: "2026-07-31"
gate: "VF-VHQ-W5-OPERATIONS-BUS"
founder_go: true
founder_go_note: "Implement authorized by Founder plan accept + Implement instruction 2026-07-31"
prod_baseline: "6375ab1 / vhq-w40c"
runtime_ui_tip: "5ba9f8d"
cache_target: "vhq-w50a"
commit: false
deploy: false
close: "docs/handoffs/2026-07-31-VF-VHQ-W5-OPERATIONS-BUS-CLOSE.md"
---

# BLAST — VF-VHQ-W5-OPERATIONS-BUS

**Date:** 2026-07-31  
**Backlog:** `VF-VHQ-W5-OPERATIONS-BUS`  
**Class:** Feature — data integration (SQLite bus + thin Commander UI)  
**Surface (1-1-1):** `lead_qualified` → `wizard_started` → `order_created` (+ approval hooks)  
**Founder GO implement:** yes (plan accept + Implement)  
**Prod baseline (unchanged until deploy GO):** tip `6375ab1` · UI `5ba9f8d` · cache `vhq-w40c`  
**Cache target (local):** `vhq-w50a`

---

## B — Background (Why)

| Field | Value |
|-------|-------|
| Trigger | W4 CLOSED + INC-SSH CLOSED; session lock → W5 plan then implement |
| Value | Typed Operations Bus on cash spine with audit; no agent-chat workflow |
| Program SoT | `docs/ops/FLEXGRAFIK-VIRTUAL-HQ-PROGRAM.md` §7 W5 |
| Architecture | `docs/ops/FLEXGRAFIK-VIRTUAL-HQ-ARCHITECTURE.md` §8 catalog · §10 BusEvent |
| Design | `VHQ-INTERACTION-SPEC.md` §6 · `OperationsFlowLine` / `DepartmentHandoffCard` |
| Honesty residual | Order Desk **PARKED** **EV-W2-010** — preserve; INT-002 ≠ desk SoT |

**Decision (locked):** `ops_bus_events` + `agent/ops_bus/` + hooks on disposition / sales_cta / order first-insert + JWT list/ingest + thin UI trail. Do not overload `brain_events`. Do not flip Order LIVE.

---

## L — Limits & invariants

### In scope

- Events: `lead_qualified`, `wizard_started`, `order_created`, `approval_needed` (L2 companion)
- Idempotent emit · audit via `append_audit` · kill-switch `ops_bus_enabled`
- Thin UI: flow/handoff/order trail; cache `vhq-w50a`
- Evidence EV-W5-001…005

### Out / Hard STOP

- Free-form agent chat bus · silent L3/L4 · Ads/Mollie/Gate D
- Fake Order LIVE / drop EV-W2-010
- Production spine events · W6 Vault UX · MKT dirty
- Deploy without separate Zasada 11 GO

### Invariants

- `VHQ_ROOMS` sole status SoT · HQ primary · 5 tabs · D0.10 audit chain
- Commercial break at Order PARKED remains visible

---

## A — Actions (`/implement`)

### S1 Schema + module

- [x] `_init_ops_bus_schema` in `agent/db.py`
- [x] `agent/ops_bus/{catalog,emit,flags}.py`
- [x] Unit: idempotent / unknown type / flag off

### S2 Emitters + audit

- [x] `post_lead_disposition` acked → `lead_qualified`
- [x] `spawn_brief_sales_cta_tickets` → `lead_qualified` + `wizard_started`
- [x] `process_order_webhook` first insert → `order_created`
- [x] `append_audit` on every successful emit

### S3 API + approval hooks

- [x] GET `/api/v1/commander/ops-bus/events`
- [x] POST `/api/v1/commander/ops-bus/ingest` (typed `wizard_started`)
- [x] POST approval L2 state-only; L3/L4 → 403

### S4 UI honesty

- [x] Bind handoff/trail from bus API
- [x] Preserve EV-W2-010 on all Order surfaces
- [x] Wizard CTA beacon · cache `vhq-w50a`

---

## S — Binary DoD

- [x] D1 `ops_bus_events` + CHECKs
- [x] D2 `lead_qualified` from disposition acked + audit
- [x] D3 `wizard_started` from CTA/beacon
- [x] D4 `order_created` insert-only
- [x] D5 audit chain valid (EV-W5-004)
- [x] D6 L2 pending; L3/L4 403
- [x] D7 Order PARKED EV-W2-010
- [x] D8 GET JWT; flag off → empty
- [x] D9 typed UI; no chat/fake KPI
- [x] D10 EV-W5-001…005 + pytest green (`test_ops_bus` 9/9)

---

## Staging list (W5-only)

```text
agent/db.py
agent/ops_bus/**
agent/nodes/order_node.py
agent/nodes/brief_node.py
api/routes/ops_bus.py
api/app.py
commander-ui/app.js
commander-ui/index.html
commander-ui/styles.css
commander-ui/sw.js
tests/unit/test_ops_bus_*.py
tests/unit/test_wc_order_webhook.py
todo.json
docs/handoffs/2026-07-31-VF-VHQ-W5-OPERATIONS-BUS-BLAST.md
```

**Never stage:** `docs/ops/marketing/**`

---

## Rollback

1. `ops_bus_enabled=false` in commander_settings  
2. UI falls back to static `VHQ_ROOMS` flow  
3. Git revert; tip `6375ab1` / `vhq-w40c`  
4. Do not DROP table on prod without GO  

---

BLAST_VERDICT: **CLOSED locally** — dogfood PASS · CLOSE stamped · deploy needs separate GO.
