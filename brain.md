---
status: "[ACTIVE]"
title: "Jadzia-Core Brain (Canonical)"
owner: "Norbert Wozniak"
updated: "2026-06-26"
readiness_overall: "~40% vs COI vision"
---

## 1) Misja modułu

**TO-BE (wizja):** Jadzia jako **Chief Operating Intelligence (COI)** — prawa ręka Dowódcy: sense → think → plan → act → guard (Kaizen).

**AS-IS (dziś, uczciwie):** FastAPI backend na VPS z trzema filarami LIVE:
- WP code agent (SSH read/write/rollback) via Telegram + worker queue + HITL
- Customer sales chat widget dla Wizarda (INT-001)
- Task/session management w SQLite (`jadzia.db`)

Szczegóły charter: `flexgrafik-meta/docs/core/jadzia-operating-charter.md`

## 2) AS-IS LIVE (kod potwierdzony)

| Capability | Entry point | Status |
|------------|-------------|--------|
| WP edit pipeline | `core/agent.py` → `agent/nodes/*` → SSH | LIVE |
| Worker queue + HITL | `api/routes/worker.py`, JWT | LIVE |
| Wizard widget chat | `POST /api/v1/widget/chat` | LIVE |
| Telegram ops | `api/telegram.py` | LIVE |
| LLM client | `core/llm.py` (Haiku/Sonnet) | LIVE |
| Session state | `agent/state/` + `agent/db.py` | LIVE (SQLite-only) |
| Cost tracking | `api/routes/costs.py` | LIVE |

**Pipeline:** `routing → commands | intent | planning | generate | approval → SSH write → HITL diff`

## 3) TO-BE Phase A (następna fala — COI Revenue)

| Element | Kontrakt | Status |
|---------|----------|--------|
| Order ingestion | INT-002 `POST /webhooks/woocommerce/order` | LIVE |
| `order_node` | `agent/nodes/order_node.py` | LIVE |
| `orders` table | `jadzia.db` — `agent/db.py` | LIVE |

Plan wykonania: `docs/plans/PLAN-COI-PHASE-A.md`

## 4) Dane

- **Operational SSoT:** `data/jadzia.db` (SQLite-only — brak JSON session files)
- **Agent tasks/sessions:** `agent/db.py`, `agent/state/`
- **Customer chat:** TTLCache w `agent/customer_agent.py`
- **Orders/leads/calendar:** PLANNED (Phase A/B)

## 5) Integracje

| ID | Kierunek | Status |
|----|----------|--------|
| INT-001 | Wizard → widget chat | LIVE |
| INT-002 | WC → order webhook | LIVE (receiver); zzpackage sender P0-03 |
| INT-003 | Game → Wizard coupon | LIVE (app side) |
| Game lead sync | app → jadzia `POST /api/v1/leads` | LIVE (receiver); DEPLOY-02 E2E pending |

Pełne kontrakty: `flexgrafik-meta/docs/core/integration-contracts.md`

## 6) Readiness vs wizja COI

| Dimension | AS-IS | TO-BE |
|-----------|-------|-------|
| WP SSH agent | 90% | 95% |
| Customer chat | 85% | 90% |
| Worker queue/HITL | 85% | 90% |
| Operational OS (orders/leads) | 5% | 90% |
| Analytics integration | 0% | 80% |
| Content calendar | 0% | 75% |
| COI strategy synthesis | 10% (docs) | 85% |
| **Overall** | **~40%** | **85%** |

## 7) Source of Truth

- **Module spec (COI):** `flexgrafik-meta/docs/core/modules/module-jadzia-core.md`
- **Charter:** `flexgrafik-meta/docs/core/jadzia-operating-charter.md`
- **Strategia makro:** `flexgrafik-meta/docs/core/master-plan.md`
- **Globalne zasady:** `flex-vcms/docs/core/global-rules.md`
- **Workflow:** `.agents/workflows/README.md` (L0-L4)
- **Backlog:** `todo.json`
- **PRD:** `docs/PRD-core.md`
- **Plan aktywny:** `docs/plans/PLAN-COI-PHASE-A.md`

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
Latest docs/handoffs/*.md
```
