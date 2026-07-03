# PRD-core.md — jadzia-core

*Version: 2.1 | Owner: Norbert Wozniak | Updated: 2026-07-03*

Canonical module spec: `flexgrafik-meta/docs/core/modules/module-jadzia-core.md`

---

## Project description

**TO-BE:** Chief Operating Intelligence (COI) for FlexGrafik ecosystem.

**AS-IS:** FastAPI backend on VPS — WP SSH agent, Wizard sales widget, worker/HITL queue.

VPS: `185.243.54.115:8000` (Ubuntu, systemd `jadzia.service`)
Paths: `/opt/jadzia` + user `jadzia` (OPS-01 DONE; see `deployment/jadzia.service`)

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
| `lead_node` | P1 | Game lead API | LIVE (DEPLOY-02 E2E PASS) |
| `analytics_node` | P1 | GA4 snapshot (INT-009) | LIVE (DEPLOY-03 E2E PASS) |
| `content_calendar_node` | P2 | Social schedule (INT-010) | LIVE |
| Facebook publish | P2 | INT-011 Graph API `POST /feed` | LIVE (B3 E2E PASS 2026-07-01) |

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
User: jadzia (OPS-01 DONE)
Service: jadzia.service
Path: /opt/jadzia

Deploy flow (manual — Zasada 11):
  1. Backup: cp data/jadzia.db data/jadzia.db.bak.$(date +%Y%m%d-%H%M%S)
  2. Upload code (exclude data/, .env, venv/)
  3. pip install -r requirements.txt  # or requirements.lock when present
  4. systemctl restart jadzia
  5. curl -f http://localhost:8000/worker/health

Production service runs: uvicorn main:app (no reload). Local dev: UVICORN_RELOAD=1 python main.py

Runbook: deployment/deploy-to-vps.sh
```

### Production security (S2-01)

Set on VPS `.env`:

| Env | Purpose |
|-----|---------|
| `JADZIA_ENV=production` or `REQUIRE_SECRETS=1` | Fail boot if secrets missing |
| `JWT_SECRET` | Worker + admin routes (`/chat`, `/rollback`, `/logs`, …) |
| `WC_WEBHOOK_SECRET` | INT-002 HMAC (match zzpackage wp-config) |
| `LEADS_API_KEY` | INT-004 X-API-Key |

Public by design: `/api/v1/widget/chat`, `/api/v1/portal/qualify`, health probes.

### INT-011 Facebook Page publish (Phase B.3)

| Env | Purpose |
|-----|---------|
| `FB_PAGE_ID` | Facebook Page ID (FlexGrafik: `491325420727745`) |
| `FB_ACCESS_TOKEN` | Page Access Token — **VPS .env only, never commit** |
| `FB_PUBLISH_CHECK_INTERVAL_SECONDS` | Worker scheduled publish check (default 60, 0=off) |

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/content-calendar/{entry_id}/publish` | Publish approved facebook entry |
| GET | `/api/v1/content-calendar/{entry_id}/publish-status` | `fb_post_id`, `publish_result` |

E2E: `deployment/deploy-b3-fb-publish-e2e.sh`

**Roadmap after B3:** B3.1 insights, B3.2 read comments, B3.3 reply HITL — see `docs/handoffs/2026-06-30-b3-fb-publish-implementation.md`

---

## AI guidelines

- Schema change → `/migrate` workflow first; update PRD + tests together
- Feature branch preferred; pytest after every change
- One node at a time (1-1-1)
- Active plan: `docs/plans/PLAN-COI-PHASE-B.md`
- Do not claim LangGraph — use custom pipeline until explicit migration decision
