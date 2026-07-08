---
status: "[ACTIVE]"
title: "Jadzia-Core Brain (Canonical)"
owner: "Norbert Wozniak"
updated: "2026-07-08"
readiness_overall: "~85% operational spine"
---

## 1) Misja modułu

**TO-BE (wizja):** Jadzia jako **Chief Operating Intelligence (COI)** — prawa ręka Dowódcy: sense → think → plan → act → guard (Kaizen).

**AS-IS (dziś, uczciwie):** FastAPI backend na VPS z trzema filarami LIVE:
- WP code agent (SSH read/write/rollback) via Telegram + worker queue + HITL
- Customer sales chat widget dla Wizarda (INT-001)
- Task/session management w SQLite (`jadzia.db`)

Szczegóły charter: `flexgrafik-meta/docs/core/jadzia-operating-charter.md`

## 2) AS-IS LIVE (kod potwierdzony, 2026-06-30)

| Capability | Entry point | Status |
|------------|-------------|--------|
| WP edit pipeline | `core/agent.py` → `agent/nodes/*` → SSH | LIVE |
| Worker queue + HITL | `api/routes/worker.py`, JWT | LIVE |
| Wizard widget chat | `POST /api/v1/widget/chat` | LIVE |
| Telegram ops | `api/telegram.py` | LIVE |
| LLM client | `core/llm.py` (Haiku/Sonnet) | LIVE |
| Session state | `agent/state/` + `agent/db.py` | LIVE (SQLite-only) |
| Cost tracking | `api/routes/costs.py` | LIVE |
| Content calendar | `agent/nodes/content_calendar_node.py` | LIVE |
| Weekly COI brief | `agent/nodes/brief_node.py` | LIVE (worker hook) |
| Portal qualification | `api/routes/portal_qualify.py` | LIVE (INT-012) |
| **Management CLI** | `cli/main.py` → `jadzia` cmd | LIVE (5 cmds) |
| Design Agent INSPIRE v2 | `api/routes/design_agent.py` | LIVE (separate track — handoff 2026-07-08) |

**Pipeline:** `routing → commands | intent | planning | generate | approval → SSH write → HITL diff`

**VPS runtime:** `jadzia` user (non-root), `/opt/jadzia`, systemd `jadzia.service`

## 3) COI Phase A (kod agenta — COMPLETE)

| Element | Kontrakt | Status |
|---------|----------|--------|
| Order ingestion | INT-002 `POST /webhooks/woocommerce/order` | LIVE (WC order 3149 on prod) |
| `order_node` | `agent/nodes/order_node.py` | LIVE |
| `orders` table | `jadzia.db` — `agent/db.py` | LIVE |
| Lead ingestion | INT-004 `POST /api/v1/leads` | LIVE (DEPLOY-02 E2E PASS) |
| `lead_node` | `agent/nodes/lead_node.py` | LIVE |
| `leads` table | `jadzia.db` | LIVE |
| Analytics snapshot | INT-009 `GET /api/v1/analytics/snapshot` | LIVE (GA4 on VPS; prod-smoke 8/8) |
| `analytics_node` | `agent/nodes/analytics_node.py` | LIVE |
| Content calendar | INT-010 `GET/POST/PATCH /api/v1/content-calendar` | LIVE (VPS) |
| `content_calendar_node` | `agent/nodes/content_calendar_node.py` | LIVE |
| Facebook publish | INT-011 `POST/GET …/publish` | LIVE (VPS E2E PASS 2026-07-01) |

Plan Phase A (completed): `docs/archive/plans/PLAN-COI-PHASE-A.md`  
Plan Phase B (completed): `docs/archive/plans/PLAN-COI-PHASE-B.md`

## 4) Dane

- **Operational SSoT:** `data/jadzia.db` (SQLite-only — brak JSON session files)
- **Agent tasks/sessions:** `agent/db.py`, `agent/state/`
- **Customer chat:** TTLCache w `agent/customer_agent.py`
- **Orders/leads:** LIVE w `jadzia.db` (Phase A kod)
- **Analytics:** GA4 read-through cache + **SQLite persist** (`analytics_snapshots`, S3-01)
- **Content calendar:** LIVE w `jadzia.db` (Phase B bootstrap)

## 5) Integracje

| ID | Kierunek | Status |
|----|----------|--------|
| INT-001 | Wizard → widget chat | LIVE |
| INT-002 | WC → order webhook | LIVE |
| INT-003 | Game → Wizard coupon | LIVE (app side) |
| INT-004 | app → `POST /api/v1/leads` | LIVE (DEPLOY-02 E2E PASS) |
| INT-009 | GA4 → analytics snapshot | LIVE |
| INT-010 | Content calendar | LIVE (VPS) |
| INT-011 | Facebook publish | LIVE (VPS E2E 2026-07-01) |
| INT-012 | Portal qualification | LIVE (2026-06-25) |

Pełne kontrakty: `flexgrafik-meta/docs/core/integration-contracts.md`

## 6) Readiness vs wizja COI

| Dimension | AS-IS | TO-BE |
|-----------|-------|-------|
| WP SSH agent | 90% | 95% |
| Customer chat | 85% | 90% |
| Worker queue/HITL | 85% | 90% |
| Operational OS (orders/leads) | 85% | 90% |
| Analytics integration | 80% | 80% |
| Content calendar | 75% | 75% |
| COI strategy synthesis | 40% (brief LIVE; no auto-spawn) | 85% |
| **Overall** | **~85%** operational spine | **85%** full COI vision |

## 7) Source of Truth

- **Module spec (COI):** `flexgrafik-meta/docs/core/modules/module-jadzia-core.md`
- **Charter:** `flexgrafik-meta/docs/core/jadzia-operating-charter.md`
- **Strategia makro:** `flexgrafik-meta/docs/core/master-plan.md`
- **Globalne zasady:** `flex-vcms/docs/core/global-rules.md`
- **Workflow:** `.agents/workflows/README.md` (L0-L4)
- **Backlog:** `todo.json`
- **PRD:** `docs/PRD-core.md`
- **Active plan:** `docs/superpowers/specs/2026-07-08-jadzia-spine-closure-design.md`

## 8) Workflow Framework (v2.0)

Golden Path: **L0 Triage → L1 Design → L2 Execute → L3 Validate → L4 Release**

| Layer | Komenda | Cel |
|-------|---------|-----|
| L0 | `/vibe-init` | Triage, klasyfikacja |
| L1 | `/blast` | Feature — kontrakt techniczny |
| L1 | `/blueprint` | Refactor — mapowanie |
| L2 | `/implement` | Kod |
| L3 | `/jadzia-test` | Pytest + smoke |
| L4 | `/handoff` | Zamknięcie sesji |

## 9) Guardrails

- Deploy produkcja: **manual** (Zasada 11)
- Zasada 1-1-1: jedna sesja = jedno zadanie = jeden handoff
- Brak commitu w repo produktowych przez COI runtime (to Cursor/Agent OS)
- Min checkout 199 EUR, marża 60% — Wizard-only

## 10) Context Packet (sesja agenta)

```
brain.md
todo.json
docs/PRD-core.md
.agents/workflows/README.md
flexgrafik-meta/docs/core/jadzia-operating-charter.md
Latest docs/handoffs/README.md (then last 2 dated handoffs)
```
