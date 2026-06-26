# PLAN-COI-PHASE-B — Content Calendar bootstrap

**Status:** IN PROGRESS (P2-01 kod done)  
**Created:** 2026-06-26  
**Parent:** `docs/plans/PLAN-COI-PHASE-A.md` (code complete)  
**Contract:** INT-010

---

## Goal

Internal social content calendar in `jadzia.db` — FB/TikTok drafts, approval workflow, case-study suggestions from orders.

**Out of scope (Phase B.2):** actual FB/TikTok API publish, Telegram reminders cron.

---

## Delivered (P2-01)

| Item | Path |
|------|------|
| Schema | `content_calendar` table — `agent/db.py` |
| Node | `agent/nodes/content_calendar_node.py` |
| API | `GET/POST/PATCH /api/v1/content-calendar` + suggestions |
| Auth | JWT (`verify_jwt`) |
| Tests | `test_calendar_store`, `test_content_calendar_node`, `test_content_calendar_api` |

---

## API contract

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/content-calendar` | List entries (`status`, `platform` filters) |
| POST | `/api/v1/content-calendar` | Create draft |
| PATCH | `/api/v1/content-calendar/{entry_id}` | Update copy/status |
| GET | `/api/v1/content-calendar/suggestions/orders` | Case-study ideas from `orders` |

**Status flow:** `draft` → `pending_approval` → `approved` → `published` | `cancelled`

---

## Next (Phase B.2)

1. Telegram notify on `pending_approval`
2. FB/TikTok API integration (separate dep audit)
3. Scheduled publish job (worker loop extension)

---

## Regression

```bash
pytest tests/ -q
curl -H "Authorization: Bearer $JWT" http://localhost:8000/api/v1/content-calendar
```
