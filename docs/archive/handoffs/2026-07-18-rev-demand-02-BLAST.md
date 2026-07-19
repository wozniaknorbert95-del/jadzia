# BLAST — REV-DEMAND-02 Widget session durability

**Date:** 2026-07-18  
**Repo:** jadzia-core  
**Branch:** master @ `092f814` (02a LIVE)  
**Backlog:** `REV-DEMAND-02`

## B — Background

Widget chat history lives only in `TTLCache` → lost on restart / process recycle.  
Breaks mid-funnel CTA continuity (Demand path).

## L — Limits

- No Gate D / Mollie / min199
- No park deletes; do not ship `_recover_*.py`
- Do not change CTA score gate (02a)
- Deploy only after Dowódca GO
- SQLite = SSoT (not separate /tmp DB)

## A — Actions

- [ ] `agent/db.py` — table `widget_chat_sessions` + get/save/delete
- [ ] `agent/customer_agent.py` — L1 TTLCache + L2 SQLite load/save (TTL 24h)
- [ ] `tests/unit/test_widget_session_durability.py` — persist, TTL expire, cache-miss reload
- [ ] Handoff + todo; await GO redeploy

## S — Success

- [ ] History survives cache clear (simulates restart)
- [ ] Expired sessions (>24h) return empty / deleted
- [ ] Existing CTA + widget tests still green
- [ ] Request still succeeds if SQLite write fails (log + cache)

## T — Test plan

- Unit: DB roundtrip, expire, hybrid reload after cache clear
- Smoke post-GO: two widget turns, restart service, third turn keeps context (optional)

```text
BLAST_ANCHOR: docs/handoffs/2026-07-18-rev-demand-02-BLAST.md
BACKLOG_ID: REV-DEMAND-02
INVARIANTS_TO_PROTECT: parks, Gate D, 02a CTA gate, no _recover ship
---
CURRENT_STAGE: L1 → implement (senior decide)
---
```
