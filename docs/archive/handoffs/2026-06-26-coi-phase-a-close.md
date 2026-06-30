# Handoff — COI Phase A code complete + deploy routing

**Date:** 2026-06-26  
**Stage:** L4-Closed (agent code wave)  
**Active gates:** DEPLOY-01 (Mollie), DEPLOY-03 (GA4) — human

---

## P1-02 verification audit (plan vs kod)

| Plan item | Status | Evidence |
|-----------|--------|----------|
| Ścieżka C (app + zzpackage) | PASS | `ga4_client.fetch_app_metrics` + `fetch_zzpackage_metrics` |
| `agent/nodes/analytics_node.py` | PASS | TTL cache, degradacja, partial fail |
| `core/ga4_client.py` | PASS | Data API, event filters (`game_start`, `lead_captured`, `score_submitted`) |
| `GET /api/v1/analytics/snapshot` | PASS | `api/routes/analytics.py`, period `1d\|7d\|30d` |
| JWT auth | PASS | `Depends(verify_jwt)` |
| Pydantic models | PASS | `core/models.py` — `AnalyticsSnapshotResponse` |
| Router registered | PASS | `api/app.py` L52-63 |
| `google-analytics-data` dep | PASS | `pyproject.toml`, `requirements.txt` |
| Unit tests | PASS | 9 tests — node + API |
| Integration route test | PASS | `test_api_integration.py` |
| Full regression | PASS | `pytest tests/ -q` — 332 passed |
| Handoff P1-02 | PASS | `docs/handoffs/2026-06-26-p1-02-analytics-node.md` |
| todo P1-02 completed | PASS | `todo.json` |
| PRD updated | PASS | `docs/PRD-core.md` analytics_node LIVE |
| Brak SQLite table | PASS | read-through cache only |
| Degraded bez GA4 → HTTP 200 | PASS | `test_analytics_snapshot_degraded_without_ga4` |
| Total fail → HTTP 503 | PASS | `test_analytics_snapshot_fail_returns_503` |
| flexgrafik-nl analytics | DEFERRED | Phase B (per plan) |
| `wizard_step_view` funnel | DEFERRED | P1.1 optional per plan |
| INT-009 meta → LIVE | PENDING | po DEPLOY-03 proof |
| Prod deploy | PENDING | Dowódca — Zasada 11 |

**Verdict:** P1-02 kod w 100% zgodny z planem MVP. Brakuje tylko deploy proof (human).

---

## COI Phase A — kod agenta: COMPLETE

| Task | Status |
|------|--------|
| P0-01 order_node | completed |
| P0-02 orders schema | completed |
| P0-03 WC webhook (zzpackage) | completed |
| P1-01 lead_node | completed |
| P1-02 analytics_node | completed |

---

## Deploy queue (kolejność Dowódcy)

```text
1. DEPLOY-01  INT-002 Mollie E2E     → docs/handoffs/2026-06-26-deploy-int-002-proof.md
2. DEPLOY-03  INT-009 GA4 snapshot  → docs/plans/PLAN-DEPLOY-INT-009.md
3. DEPLOY-02  INT-004 lead E2E      → gdy app wysyła POST /api/v1/leads
```

DEPLOY-01 i DEPLOY-03 mogą iść równolegle po zamknięciu Mollie (niezależne sekrety).

---

## Następna fala (Phase B — nie teraz)

- `content_calendar_node` + INT-010
- flexgrafik-nl GA4 (3. property)
- `wizard_step_view` w zzpackage snapshot (P1.1)
- OPS-01 VPS user `jadzia@/opt/jadzia`
- S1-01 secret rotation

---
RECOMMENDED_NEXT: DEPLOY-01 Mollie → DEPLOY-03 GA4 credentials
WHY_NEXT: Phase A kod gotowy; brakuje tylko prod proof na dwóch gate'ach
