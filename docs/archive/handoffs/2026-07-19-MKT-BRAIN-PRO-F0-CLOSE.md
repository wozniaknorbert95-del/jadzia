---
status: "[ACTIVE]"
title: "MKT-BRAIN-PRO F0 — Data Truth Layer CLOSE"
gate: "MKT-BRAIN-PRO-F0"
updated: "2026-07-19"
result: "PASS (ops degraded: GA4 env missing on VPS)"
tip: "f28a938"
---

# MKT-BRAIN-PRO F0 — CLOSE

## Git / tip

| Pole | Wartość |
|------|---------|
| Branch | `master` |
| Tip | `f28a938` |
| Commit | `feat(mkt-brain): F0 Data Truth Layer — schema, ingest, Data Health` |
| Backup VPS | `/opt/jadzia/data/jadzia-pre-mkt-brain-f0-20260719-143314.db` |

## Evidence

| Check | Result |
|-------|--------|
| pytest `tests/unit/test_dtl_f0.py` | **9/9 PASS** |
| Push `origin/master` | **PASS** `b8c74df..f28a938` |
| VPS `git reset --hard origin/master` | **PASS** tip `f28a938` |
| `systemctl is-active jadzia` + `/health` | **PASS** |
| DTL tables in SQLite | **PASS** (4/4) |
| Manual ingest POST | **PASS** steps_ok=5 steps_error=1 |
| Margin coverage | **PASS** 36/36 = 100% |
| Facts written | **PASS** facts=53 raw=16 |
| Data Health API | **PASS** panel + freshness keys |
| `MARKETING_DTL_INGEST_INTERVAL_SECONDS` | **set** `3600` on VPS `.env` |

## Honest gaps (not fake PASS)

| Item | Status |
|------|--------|
| GA4 ingest on VPS | **FAIL / degraded** — `is_ga4_configured()=False` (brak `GA4_PROPERTY_ID_*` / creds w runtime env). Quality flag `api_error` RED — expected. |
| L0 events fire | **amber** — HTML probe OK; InitiateCheckout/Purchase = Events Manager (human / META-PACK) |
| 7d continuous ingest | **STARTED** — worker interval 3600s; observe in Commander Data Health |

## Surface

- `agent/marketing/dtl/*`
- `GET /api/v1/commander/marketing/data-health`
- `POST /api/v1/commander/marketing/dtl/ingest`
- Commander UI: Analityka → Data Health

## PARK / next

- **ready_for_human:** uzupełnij GA4 env na VPS (property IDs + `GOOGLE_APPLICATION_CREDENTIALS`) → re-ingest → overall ≠ red
- **META-PACK-LEAN L0** — równolegle Dowódca (Events Manager)
- **F1** — Shadow + Telegram proposals (blocked until F0 observation OK)

## Deploy note

VPS miał dirty working tree przed pull — rozwiązane `rm agent/marketing` + `git reset --hard origin/master` (po SQLite backup).
