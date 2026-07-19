# BLAST — REV-DEMAND-03 INSPIRE → lead bridge

**Date:** 2026-07-18  
**Repo:** jadzia-core  
**VPS tip:** `644b34e` (02 LIVE)  
**Backlog:** `REV-DEMAND-03`

## B — Background

INSPIRE chat has no durable lead path. Widget already persists on email+consent.  
Bridge: same gate → `db_create_lead(source=inspire)` → `lead_id` in chat response.

## L — Limits

- No Gate D / Mollie / min199
- No park deletes; no `_recover_*.py`
- No REV-DEMAND-04 / B3 in this slice
- Deploy only after GO

## A — Actions

- [ ] `chat_advisor.py` — email/consent helpers + persist after turn (both engines)
- [ ] `ChatTurnResult` + `DesignAgentChatResponse` + `_to_response` → `lead_id`
- [ ] Tests: no email / no consent / email+consent → lead
- [ ] Handoff; await GO

## S — Success

- [ ] email+consent → `leads` row `source=inspire`, response `lead_id`
- [ ] missing either → `lead_id=null`, no row
- [ ] orchestrator + legacy covered via `process_chat_turn` wrapper
- [ ] pytest green

```text
BLAST_ANCHOR: docs/handoffs/2026-07-18-rev-demand-03-BLAST.md
BACKLOG_ID: REV-DEMAND-03
---
CURRENT_STAGE: implement
---
```
