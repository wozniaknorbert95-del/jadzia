# OPS AI Scorecard — ≥60% pracy operacyjnej

**Status:** ACTIVE — COI-OPS-AI-00 baseline protocol; COI-OPS-AI-01 interim  
**Date:** 2026-07-18  
**Window:** 14 dni kalendarzowych

## Formuła

```text
ops_ai_ratio = ai_executed_ops / (ai_executed_ops + human_executed_ops)
target ≥ 0.60
```

CRITICAL HITL (human must approve CRITICAL) **nie** obniża score jako „porażka AI” — te zdarzenia są wyłączone z mianownika (`excluded_critical_hitl`).

## Klasyfikacja zdarzeń

| Klasa | Przykłady | Licznik |
|-------|-----------|---------|
| AI executed | widget reply, auto lead create, brief spawn tickets, FB publish job (po approve), Agent OS agent run | `ai_executed_ops` |
| Human executed | disposition Ack/Snooze/Close, marketing approve click, manual settings, VCMS conflict resolve | `human_executed_ops` |
| Excluded | CRITICAL ticket approve/reject | `excluded_critical_hitl` |

## Baseline protocol (OPS-AI-00)

| Field | Value |
|-------|-------|
| Measurement start | 2026-07-18 |
| First full window end | 2026-08-01 |
| Method | Commander audit-log actions + lead dispositions + marketing approve + widget sessions (VPS query) |
| Interim estimate (architecture) | Widget+brief+queue auto-path dominates daily ops; human primarily Ack/publish — **expected ≥60% when measured**; not a PASS until window closes with numbers |

## OPS-AI-01 — Cel ≥60%

| Field | Value |
|-------|-------|
| Status | **INTERIM** — instrumentation + policy LIVE; numerical PASS deferred to 2026-08-01 |
| Safety | CRITICAL HITL retained |
| Evidence required | Export counts into this file under „Window results” |

### Window results (fill after 14d)

| Window | ai | human | excluded | ratio | PASS? |
|--------|----|-------|----------|-------|-------|
| 2026-07-18 → 2026-08-01 | TBD | TBD | TBD | TBD | pending |

### VPS measurement sketch (no secrets)

```bash
# On /opt/jadzia — count audit actions / dispositions in last 14d (adapt SQL to schema)
sudo -u jadzia sqlite3 data/jadzia.db "SELECT action, COUNT(*) FROM commander_audit_log WHERE ts >= datetime('now','-14 days') GROUP BY action;"
```

## Automation safe list (toward 60%)

Allowed without extra HITL: widget replies, lead scoring, brief INFO spawns, freshness polls.  
Always HITL: CRITICAL queue, public marketing publish, deploy, Gate D, payment.
