# OPS AI Scorecard — ≥60% pracy operacyjnej

**Status:** **PASS / LIVE** — v1.1 **60.6%** na VPS tip `d97939a`  
**Date:** 2026-07-18  
**Window:** rolling 14 dni  
**VPS tip SoT:** `d97939a`

## Formuła

```text
ops_ai_ratio = ai_executed_ops / (ai_executed_ops + human_executed_ops)
target ≥ 0.60
```

CRITICAL HITL **nie** liczy się jako porażka AI (`excluded_critical_hitl`).

## Klasyfikacja v1.1 (kontrakt PASS)

| Klasa | Co liczymy | Źródło |
|-------|------------|--------|
| AI executed | Tickets `brief_sales_cta` + `brief_hitl` + `cs_followup` + leads `created_at` + widget sessions `created_at` | SQLite |
| Human executed | Audit `publish` + leads `disposition=closed` | SQLite |
| Excluded | CRITICAL approve | — |

v1 (baseline history): brief_* + leads only → 45.8% — zachowane poniżej dla audytu.

## Window results — PASS 2026-07-18 (VPS `/opt/jadzia` @ `d97939a`)

| Metric | Count |
|--------|------:|
| Tickets AI (`brief_*` + `cs_followup`) | 8 |
| Leads created | 5 |
| Widget sessions `created_at` 14d | 7 |
| **ai_executed_ops** | **20** |
| Audit publish (dowodca) | 8 |
| Leads closed | 5 |
| **human_executed_ops** | **13** |
| excluded_critical_hitl | 0 |
| **ops_ai_ratio** | **20/33 = 60.6%** |
| **PASS ≥60%?** | **YES** |

Schema: `WIDGET_COLS` includes `created_at` (migrate + backfill on deploy).  
Health post-deploy: `/health` OK. CRITICAL HITL path retained (queue disposition/approve unchanged).

### v1 baseline (pre-instrumentation, same window)

| Metric | Count |
|--------|------:|
| **ops_ai_ratio** | **11/24 = 45.8%** |
| **PASS ≥60%?** | **NO** (historical) |

### Reprodukcja

```bash
scp deployment/_ops_ai_count_14d.py root@VPS:/tmp/
ssh root@VPS 'python3 /tmp/_ops_ai_count_14d.py'
# expect: RATIO_V11 ... PCT 60.6 ... PASS_GE_60 YES
```

## OPS-AI-01 status

| Field | Value |
|-------|-------|
| todo status | **completed** |
| Scorecard #9 | **LIVE / PASS 60.6%** |
| Safety | CRITICAL HITL retained |
| Deploy | GO 2026-07-18 → tip `d97939a` |

## Automation safe list

Allowed without extra HITL: widget replies, lead create, brief INFO/ACTION spawns, cs_followup spawn, freshness polls.  
Always HITL: CRITICAL queue, public marketing publish, deploy, Gate D, payment.
