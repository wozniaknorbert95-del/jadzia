---
status: COMPLETED
archived: 2026-06-30
---

# PLAN-COI-PHASE-A — jadzia-core

**Status:** COMPLETED (deploy gates closed 2026-06-26)  
**Created:** 2026-06-26  
**Source:** `flexgrafik-meta/docs/core/modules/module-jadzia-core.md` §8, `jadzia-operating-charter.md` §2 Filar 1  
**Supersedes:** `docs/plans/PLAN-REMEDIACJI.md` (completed)

---

## Goal

Move Jadzia from **~40% COI vision** (WP agent + widget) toward **Phase A bootstrap** per `to-be-target-state.md` §2.1:

- Order ingestion (Revenue Ops)
- Foundation for leads + analytics (Phase A/B)

Remediation sprint (architecture, SQLite-only, `core/`) is **done** — see archived `PLAN-REMEDIACJI.md`.

---

## Phase A scope

| Priority | Deliverable | Contract |
|----------|-------------|----------|
| **P0** | `orders` schema in `jadzia.db` | internal |
| **P0** | `order_node` + handler logic | `agent-cards-jadzia.md` |
| **P0** | `POST /webhooks/woocommerce/order` | INT-002 |
| **P0** | WC webhook config on zzpackage | Dowódca checklist |
| **P1** | `lead_node` + `POST /api/v1/leads` | INT (game sync) |
| **P1** | `analytics_node` snapshot endpoint | GA4 (read-only) |

---

## Execution order (1-1-1)

1. **P0-02** — Schema `orders` + migration (`/migrate` workflow) — **DONE**
2. **P0-01** — `order_node` + route (`/blast` → `/implement`) — **DONE**
3. **P0-03** — WC webhook on zzpackage (Dowódca) — **DONE**
4. **P1-01** — Lead API — **DONE**
5. **P1-02** — Analytics snapshot — **DONE**

## Deploy gates (human, Zasada 11)

| Gate | Contract | Plan |
|------|----------|------|
| DEPLOY-01 | INT-002 Mollie E2E | `PLAN-DEPLOY-INT-002.md` |
| DEPLOY-03 | INT-009 GA4 snapshot | `PLAN-DEPLOY-INT-009.md` |
| DEPLOY-02 | INT-004 lead E2E | `TEMPLATE-deploy-int-004-proof.md` |

Close handoff: `docs/handoffs/2026-06-26-coi-phase-a-close.md`

---

## Regression gate

```bash
pytest tests/ -q
curl http://localhost:8000/worker/health
```

Smoke after deploy: widget chat (INT-001), worker task create, webhook test payload.

---

## Out of scope (Phase B+)

- LangGraph migration (explicit decision required)
- `content_calendar_node`, `kaizen_audit_node`
- MCP tools per `agent-cards-jadzia.md`
- COI weekly strategy brief automation

---

## References

- Charter: `flexgrafik-meta/docs/core/jadzia-operating-charter.md`
- Contracts: `flexgrafik-meta/docs/core/integration-contracts.md`
- Module spec: `flexgrafik-meta/docs/core/modules/module-jadzia-core.md`
- Backlog: `todo.json`
