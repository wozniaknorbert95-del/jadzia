# SESSION CLOSE — COI Phase A+B deploy wave

**Date:** 2026-06-26  
**Stage:** L4-Closed  
**Commander:** explicit deploy + comprehensive close approval

---

## Delivered (agent) — COMPLETE

| Wave | Items |
|------|-------|
| P1-02 | `analytics_node`, GA4 client, `GET /api/v1/analytics/snapshot` |
| P2-01 | `content_calendar_node`, CRUD API INT-010 |
| P2-02 | Telegram alert on `pending_approval` |
| Deploy | VPS code upload + pip + restart (2x) |
| Tests | **342 passed** |
| Docs | PLAN Phase A/B, DEPLOY-INT-009, handoffs, meta contracts |
| Smoke | `deployment/prod-smoke.sh` on VPS |

---

## Prod verification (VPS 185.243.54.115)

| Check | Result |
|-------|--------|
| `systemctl jadzia` | active |
| `/worker/health` | healthy |
| Analytics + Calendar routes | JWT-protected (401 anon OK) |
| `content_calendar` table | exists |
| `orders` | SMOKE-1 only |
| GA4 env | **not set** |
| `WC_WEBHOOK_SECRET` | configured |
| `LEADS_API_KEY` | configured |

Run anytime on VPS:

```bash
bash /root/jadzia/deployment/prod-smoke.sh
```

---

## Gates — honest status

| Gate | Status | Owner action (~time) |
|------|--------|---------------------|
| **DEPLOY-01** Mollie E2E | **OPEN** | Wizard test order → real `order_id` in `orders` (~15 min) |
| **DEPLOY-03** GA4 | **OPEN** | Service account + property IDs in `.env` (~30 min) |
| **DEPLOY-02** leads E2E | **BLOCKED** | app → POST `/api/v1/leads` after DEPLOY-01 |

**Nie zamykam DEPLOY-01/03 bez real proof** — brak fałszywego PASS.

---

## Git

Commit + push na `master` w tej sesji (jadzia-core + flexgrafik-meta contracts).

---

## Next session

1. Dowódca: Mollie + GA4 (zamknij 2 gate'y)
2. Agent: Phase B.2 FB/TikTok publish API **lub** app lead sender (DEPLOY-02)

---
RECOMMENDED_NEXT: `bash deployment/prod-smoke.sh` na VPS po Mollie + GA4
WHY_NEXT: Jedyny brakujący proof to zewnętrzne systemy, nie kod
