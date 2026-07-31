# Handoff CLOSE — OPS-FRESHNESS-01 (DEPLOY LIVE)

**Date:** 2026-07-22  
**Status:** **LIVE** @ tip **`c210578`** (PR [#16](https://github.com/wozniaknorbert95-del/jadzia/pull/16) MERGED + VPS)  
**Cache:** `mkt-dash07`  
**PREV_SHA:** `3f7800a`  
**DTL schedule:** `MARKETING_DTL_INGEST_INTERVAL_SECONDS=3600` (confirmed via grep `.env`, no source hang)  
**standing_go_closeout:** `false`

## Root cause (closed)

False RED: business `updated_at` + `dowodca_last_active_at`. Pipeline was healthy (DTL ingest ok hourly).

## Deploy evidence

| Check | Result |
|-------|--------|
| TIP | `c210578` |
| verify | `VERIFY_OK` · `mkt-dash07`×2 |
| health | active · `/health` ok |
| PIPELINE clocks | orders/leads/worker **ok** (~30s) |
| Dogfood Start | Freshness **ok** · GA4 **ok** · summary UWAGA only for real **SLA bad 5** |
| Dogfood Analityka | GA4/ORDERS/LEADS/WORKER tiles **OK** |

URL: https://api.zzpackage.flexgrafik.nl/commander/?v=mkt-dash07

## LEFT (not this ticket)

- **OPS-FB-TOKEN-01** — Page Token + optional `read_insights` (HITL secrets)
- Agent SLA bad 5 — real signal; separate ticket if prioritized
- DTL `overall amber` — facebook_organic degraded (insights scope) — known park

## Next

Continue product work. Hard refresh `?v=mkt-dash07`. FB token = human.
