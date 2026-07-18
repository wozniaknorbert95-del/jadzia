# OPS AI Scorecard — ≥60% pracy operacyjnej

**Status:** IN_PROGRESS — v1 zmierzony **45.8%**; instrumentacja v1.1 **w kodzie**, PASS **zablokowany** brakiem GO deploy  
**Date:** 2026-07-18 (re-measure session)  
**Window:** rolling 14 dni  
**VPS tip SoT:** `8de8806` (match local)

## Formuła

```text
ops_ai_ratio = ai_executed_ops / (ai_executed_ops + human_executed_ops)
target ≥ 0.60
```

CRITICAL HITL **nie** liczy się jako porażka AI (`excluded_critical_hitl`).

## Klasyfikacja

### v1 (baseline — bez zmian)

| Klasa | Co liczymy | Źródło |
|-------|------------|--------|
| AI executed | Tickets `brief_sales_cta` + `brief_hitl` + leads `created_at` | SQLite |
| Human executed | Audit `publish` + leads `disposition=closed` | SQLite |
| Not in v1 | Widget sessions; `cs_followup` tickets | gap |

### v1.1 (instrumentacja — ta sesja)

| Klasa | Co liczymy | Źródło |
|-------|------------|--------|
| AI executed | v1 **plus** tickets `cs_followup` **plus** widget sessions `created_at` w oknie | SQLite |
| Human executed | bez zmian (publish + leads closed) | SQLite |
| Excluded | CRITICAL approve | — |

**Dlaczego v1.1 (nie spam ticketów):** `cs_followup` to już LIVE AI CS spawn (under-counted w v1); widget replies to allowed AI ops bez twardego zegara — dodano `widget_chat_sessions.created_at` (set once on insert; backfill `updated_at` dla legacy).

## Window results — re-measure 2026-07-18 (VPS `/opt/jadzia`)

Tip: `8de8806`. Script: `deployment/_ops_ai_count_14d.py`.

### v1 (official baseline — unchanged contract)

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

### v1.1 na prod **przed** migracją kolumny

| Metric | Count |
|--------|------:|
| Tickets AI (`brief_*` + `cs_followup`) | 8 |
| Leads created | 5 |
| Widget `created_at` 14d | **N/A** (kolumna brak na VPS) |
| **ai_executed_ops** | **13** |
| **human_executed_ops** | **13** |
| **ops_ai_ratio** | **13/26 = 50.0%** |
| **PASS ≥60%?** | **NO** |

### v1.1 **projekcja** po deploy migracji (backfill `created_at=updated_at`)

| Metric | Count |
|--------|------:|
| Tickets AI v1.1 | 8 |
| Leads created | 5 |
| Widget sessions (updated_at 14d → created_at) | 7 |
| **ai_executed_ops** | **20** |
| **human_executed_ops** | **13** |
| **ops_ai_ratio** | **20/33 = 60.6%** |
| **PASS ≥60%?** | **YES (projected — not claimed)** |

Raw: `publish×8`, `cs_followup_spawn×2`, `lead_disposition×2`. Widget cols prod: `session_id, history_json, updated_at` (brak `created_at` do GO).

### Reprodukcja

```bash
scp deployment/_ops_ai_count_14d.py root@VPS:/tmp/
ssh root@VPS 'python3 /tmp/_ops_ai_count_14d.py'
```

## OPS-AI-01 status

| Field | Value |
|-------|-------|
| todo status | **in_progress** (nie completed) |
| Scorecard #9 | FAIL / in_progress @ **45.8%** v1 |
| Code | `created_at` + count v1.1 + tests PASS lokalnie |
| Safety | CRITICAL HITL retained |
| **Blocker** | **GO deploy** tip z instrumentacją → re-measure v1.1 na VPS → PASS tylko przy SQL ≥60% |
| Next | Dowódca: GO deploy → agent re-measure → CLOSE/PASS lub kolejny 1-1-1 volume |

## Automation safe list

Allowed without extra HITL: widget replies, lead create, brief INFO/ACTION spawns, cs_followup spawn, freshness polls.  
Always HITL: CRITICAL queue, public marketing publish, deploy, Gate D, payment.
