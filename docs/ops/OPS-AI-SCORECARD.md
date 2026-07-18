# OPS AI Scorecard — ≥60% pracy operacyjnej

**Status:** IN_PROGRESS — baseline **zmierzony**, cel 60% **nie osiągnięty**  
**Date:** 2026-07-18  
**Window:** rolling 14 dni (snapshot poniżej)

## Formuła

```text
ops_ai_ratio = ai_executed_ops / (ai_executed_ops + human_executed_ops)
target ≥ 0.60
```

CRITICAL HITL **nie** liczy się jako porażka AI (`excluded_critical_hitl`).

## Klasyfikacja v1 (kontrakt pomiaru)

| Klasa | Co liczymy w v1 | Źródło |
|-------|-----------------|--------|
| AI executed | Tickets `brief_sales_cta` + `brief_hitl` (spawn) + leads `created_at` w oknie | SQLite |
| Human executed | Audit `publish` (actor dowodca) + leads `disposition=closed` updated w oknie | SQLite |
| Excluded | (brak CRITICAL approve w oknie) | — |
| Not in v1 yet | Widget message-level replies (brak `created_at` na sessions); Agent OS runs | gap |

## Window results — 2026-07-04 → 2026-07-18 (VPS `/opt/jadzia`)

| Metric | Count |
|--------|------:|
| Tickets AI spawn (`brief_*`) | 6 |
| Leads created | 5 |
| **ai_executed_ops** | **11** |
| Audit publish (dowodca) | 8 |
| Leads closed | 5 |
| **human_executed_ops** | **13** |
| excluded_critical_hitl | 0 |
| **ops_ai_ratio** | **11/24 = 45.8%** |
| **PASS ≥60%?** | **NO** |

Raw audit 14d: `publish×8`, `lead_disposition×1` (audit under-counts vs leads.closed=5).  
Widget sessions `updated_at` 14d: 7 (nie wliczone do v1 — brak twardego created_at).

### Reprodukcja

```bash
# lokalnie: deployment/_ops_ai_count_14d.py → scp → python3 na VPS
python3 deployment/_ops_ai_count_14d.py
```

## OPS-AI-01 status

| Field | Value |
|-------|-------|
| todo status | **in_progress** (nie completed) |
| Scorecard #9 | FAIL / in_progress |
| Safety | CRITICAL HITL retained |
| Next | osobna sesja: zwiększ AI spawn/automations **lub** popraw instrumentację widget; nie fałszuj PASS |

## Automation safe list

Allowed without extra HITL: widget replies, lead create, brief INFO/ACTION spawns, freshness polls.  
Always HITL: CRITICAL queue, public marketing publish, deploy, Gate D, payment.
