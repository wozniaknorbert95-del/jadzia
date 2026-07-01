# PLAN-COI-PHASE-B — Content Calendar bootstrap

**Status:** IN PROGRESS (P2-01 + B.2 E2E done)  
**Created:** 2026-06-26  
**Parent:** `docs/archive/plans/PLAN-COI-PHASE-A.md` (completed)  
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

## Delivered (Phase B.2 E2E — 2026-06-27)

| Step | Proof |
|------|-------|
| Order suggestions | `GET /content-calendar/suggestions/orders` → order `3149` |
| Draft create | `POST /content-calendar` → `entry_id=3`, `sync_status: success` |
| Pending approval | `PATCH` → `status: pending_approval` |
| Telegram alert | `_notify_pending_approval` → async `_send_telegram_alert_sync` (no TG error in logs) |

Script: `deployment/deploy-b2-calendar-e2e.sh` → **PASS** on VPS

---

## Next (Phase B.3)

1. ~~FB Graph API publish (INT-011)~~ — **CODE DONE** 2026-06-30; VPS E2E pending
2. B3.1 insights reader → B3.2 comments → B3.3 reply HITL
3. TikTok publish — Phase C (deferred)

Handoff: `docs/handoffs/2026-06-30-b3-fb-publish-implementation.md`  
E2E: `deployment/deploy-b3-fb-publish-e2e.sh`

---

## Regression

```bash
pytest tests/ -q
curl -H "Authorization: Bearer $JWT" http://localhost:8000/api/v1/content-calendar
```
