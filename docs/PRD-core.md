# PRD-core.md — jadzia-core

*Version: 2.0 | Owner: Norbert Wozniak | Updated: 2026-06-26*

Canonical module spec: `flexgrafik-meta/docs/core/modules/module-jadzia-core.md`

---

## Project description

**TO-BE:** Chief Operating Intelligence (COI) for FlexGrafik ecosystem.

**AS-IS:** FastAPI backend on VPS — WP SSH agent, Wizard sales widget, worker/HITL queue.

VPS: `185.243.54.115:8000` (Ubuntu, systemd `jadzia.service`)
Paths AS-IS: `/root/jadzia` | Target: `/opt/jadzia` + user `jadzia` (see `deployment/jadzia.service`)

---

## Tech stack (confirmed)

| Layer | Technology | Status |
|-------|------------|--------|
| Language | Python 3.11+ | LIVE |
| API | FastAPI + Uvicorn | LIVE |
| Orchestration | Custom node pipeline (`agent/nodes/*`) | LIVE |
| LLM | Anthropic Claude via `core/llm.py` | LIVE |
| Entry | `core/agent.py` (`process_message`) | LIVE |
| DB | SQLite `data/jadzia.db` (SQLite-only sessions) | LIVE |
| Remote ops | Paramiko SSH | LIVE |
| Auth | PyJWT (worker endpoints) | LIVE |
| Messaging | Telegram webhook | LIVE |
| LangGraph | — | PLANNED (explicit decision pending) |

---

## Architecture (AS-IS)

```
Telegram / HTTP / Widget
        ↓
    api/app.py (routes)
        ↓
  core/agent.py (process_message)
        ↓
  agent/nodes/* (routing → planning → generate → approval)
        ↓
  agent/tools/ssh_orchestrator.py → WordPress
```

Widget flow: Wizard → `POST /api/v1/widget/chat` → `agent/customer_agent.py` → Claude Haiku

---

## Pipeline (WP agent — LIVE)

```
queued → planning → reading_files → generating_code
→ diff_ready [HITL approval]
→ writing_files → completed / rolled_back
```

---

## Feature list

### CORE (LIVE)

| Feature | Evidence |
|---------|----------|
| Intent routing (Haiku/Sonnet) | `core/llm.py`, `agent/nodes/intent.py` |
| Planning + code generation | `agent/nodes/planning.py`, `generate.py` |
| SSH executor + backup | `agent/tools/ssh_orchestrator.py` |
| HITL approval | `agent/nodes/approval.py` |
| Telegram + worker API | `api/telegram.py`, `api/routes/worker.py` |
| Customer widget (INT-001) | `api/routes/chat.py` |
| Dashboard metrics | `api/routes/dashboard.py` |
| Cost tracking | `api/routes/costs.py` |

### COI nodes (Phase A)

| Node | Priority | Contract | Status |
|------|----------|----------|--------|
| `order_node` | **P0** | INT-002 WC webhook | LIVE |
| `lead_node` | P1 | Game lead API | LIVE (receiver); DEPLOY-02 E2E pending |
| `analytics_node` | P1 | GA4 snapshot | PLANNED |
| `content_calendar_node` | P2 | Social schedule | PLANNED |

### Infrastructure

| Feature | Status |
|---------|--------|
| `POST /webhooks/woocommerce/order` | LIVE |
| `orders` table in `jadzia.db` | LIVE |
| `GET /worker/dashboard` | LIVE |
| `GET /health`, `/worker/health` | LIVE |

### INT-002 target payload (from integration-contracts.md)

```json
{
  "order_id": "string",
  "status": "processing|completed",
  "items": [{"sku": "string", "qty": "number", "price": "number"}],
  "customer": {"email": "string", "name": "string"},
  "total_gross": "number (EUR)",
  "payment_id": "string (mollie)"
}
```

---

## Deploy config

```
VPS: 185.243.54.115
User: root (AS-IS) → jadzia (target)
Service: jadzia.service
Path: /root/jadzia (AS-IS) → /opt/jadzia (target)

Deploy flow (manual — Zasada 11):
  1. Backup: cp data/jadzia.db data/jadzia.db.bak.$(date +%Y%m%d-%H%M%S)
  2. Upload code (exclude data/, .env, venv/)
  3. pip install -r requirements.txt
  4. systemctl restart jadzia
  5. curl -f http://localhost:8000/worker/health

Runbook: deployment/deploy-to-vps.sh
```

---

## AI guidelines

- Schema change → `/migrate` workflow first; update PRD + tests together
- Feature branch preferred; pytest after every change
- One node at a time (1-1-1)
- Active plan: `docs/plans/PLAN-COI-PHASE-A.md`
- Do not claim LangGraph — use custom pipeline until explicit migration decision
