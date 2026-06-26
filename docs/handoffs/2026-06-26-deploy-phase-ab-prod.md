# Handoff — Deploy Phase A+B + Phase B bootstrap

**Date:** 2026-06-26  
**Stage:** L4-Deploy (code on VPS)  
**Commander approval:** explicit deploy + Phase B go

---

## Deploy wykonany (agent)

| Step | Result |
|------|--------|
| tar upload → `/root/jadzia` | OK |
| `pip install -r requirements.txt` | OK (`google-analytics-data` installed) |
| `systemctl restart jadzia` | OK |
| Health | `status: healthy`, worker_loop alive |
| `content_calendar` table | auto-created on VPS SQLite |
| Analytics route | HTTP 401 without JWT (expected) |
| Calendar route | HTTP 401 without JWT (expected) |

**Nie nadpisano:** `.env`, `data/jadzia.db` (poza schema migrate on connect)

---

## Gate status po deploy

| Gate | Status | Co zostaje Dowódcy |
|------|--------|-------------------|
| DEPLOY-01 INT-002 Mollie | OPEN | Wizard test order → `orders` row |
| DEPLOY-03 INT-009 GA4 | OPEN | GA4 SA + property IDs w `.env` |
| DEPLOY-02 INT-004 leads | BLOCKED | app → POST leads |
| P2-01 content_calendar kod | DONE | JWT smoke na prod |

---

## Phase B — P2-01 delivered

- `content_calendar_node` + CRUD API (INT-010 bootstrap)
- 341 pytest passed locally pre-deploy
- Plan: `docs/plans/PLAN-COI-PHASE-B.md`

---

## Prod smoke (Dowódca, ~10 min)

```bash
# JWT z JWT_SECRET
TOKEN="<jwt>"
curl -sS -H "Authorization: Bearer $TOKEN" \
  "http://185.243.54.115:8000/api/v1/analytics/snapshot"
# degraded OK bez GA4; success po DEPLOY-03

curl -sS -H "Authorization: Bearer $TOKEN" \
  "http://185.243.54.115:8000/api/v1/content-calendar"
# {"entries":[],"total":0}

curl -sS -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "http://185.243.54.115:8000/api/v1/content-calendar" \
  -d '{"platform":"facebook","title":"Test","body_nl":"NL copy","scheduled_at":"2026-07-01T10:00:00Z"}'
```

Mollie E2E: `docs/handoffs/2026-06-26-deploy-int-002-proof.md`

---
RECOMMENDED_NEXT: Mollie E2E + GA4 credentials
WHY_NEXT: Kod na VPS; brakuje tylko proof gate'ów z zewnętrznymi systemami
