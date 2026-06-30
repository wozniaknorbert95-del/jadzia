# Handoff — P1-02 analytics_node (INT-009)

**Date:** 2026-06-26  
**Stage:** L3-DiffReady (kod lokalny)  
**Gate:** DEPLOY-01 nadal OPEN (Mollie E2E = Dowódca)

## Done (agent)

| Item | Deliverable |
|------|-------------|
| P1-02 | `agent/nodes/analytics_node.py` — snapshot + TTL cache |
| GA4 client | `core/ga4_client.py` — Data API read-only |
| Route | `GET /api/v1/analytics/snapshot?period=1d\|7d\|30d` (JWT) |
| Models | `AnalyticsSnapshotResponse` w `core/models.py` |
| Dep | `google-analytics-data>=0.18.0` |
| Testy | `tests/unit/test_analytics_node.py`, `test_analytics_api.py` — 9 passed |
| Regression | `pytest tests/ -q` green |

## Scope (ścieżka C)

- **app** (`G-0XN9Z7HS90` → numeric Property ID): active_users, sessions, avg_session_duration, game_start, lead_captured, dau_1d
- **zzpackage** (`G-L23DGTEKCD` → numeric Property ID): sessions, conversions, purchase_revenue, aov
- **flexgrafik-nl** — Phase B (out of scope)

## Env (VPS — Dowódca, nie w repo)

```bash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GA4_PROPERTY_ID_APP=<numeric>
GA4_PROPERTY_ID_ZZPACKAGE=<numeric>
GA4_CACHE_TTL_SECONDS=900   # optional
```

Setup: Google Cloud → Analytics Data API → service account Viewer na obu GA4 properties.

## Deploy (manual, Zasada 11)

1. Zamknij **DEPLOY-01** (Mollie E2E) jeśli jeszcze open
2. Ustaw GA4 env na VPS `/root/jadzia/.env`
3. `./deployment/deploy-to-vps.sh` + `systemctl restart jadzia`
4. Proof:

```bash
TOKEN="<jwt>"
curl -sS -H "Authorization: Bearer $TOKEN" \
  "http://185.243.54.115:8000/api/v1/analytics/snapshot"
# sync_status: success, sources.app + sources.zzpackage
```

5. INT-009 → LIVE w `flexgrafik-meta/integration-contracts.md`

## Degradacja

- Brak GA4 env → HTTP 200, `sync_status: degraded`, `errors: ["ga4_not_configured"]`
- Partial fail → `degraded` + częściowe `sources`
- Total fail → HTTP 503

---
RECOMMENDED_NEXT: DEPLOY-01 Mollie (Dowódca) → GA4 credentials → deploy P1-02
WHY_NEXT: Kod gotowy; prod proof wymaga credentials + manual deploy
