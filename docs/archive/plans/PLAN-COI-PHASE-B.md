---
status: COMPLETED
archived: 2026-06-30
---

# PLAN-COI-PHASE-B — Content Calendar + Facebook Publish

**Status:** COMPLETED (B3 E2E PASS 2026-07-01)  
**Created:** 2026-06-26  
**Parent:** `docs/archive/plans/PLAN-COI-PHASE-A.md` (completed)  
**Contracts:** INT-010, INT-011

---

## Goal

Internal social content calendar in `jadzia.db` — drafts, approval workflow, case-study suggestions from orders, Facebook publish.

---

## Delivered (P2-01 — calendar bootstrap)

| Item | Path |
|------|------|
| Schema | `content_calendar` table — `agent/db.py` |
| Node | `agent/nodes/content_calendar_node.py` |
| API | `GET/POST/PATCH /api/v1/content-calendar` + suggestions |
| Auth | JWT (`verify_jwt`) |
| Tests | `test_calendar_store`, `test_content_calendar_node`, `test_content_calendar_api` |

---

## Delivered (Phase B.2 E2E — 2026-06-27)

| Step | Proof |
|------|-------|
| Order suggestions | `GET /content-calendar/suggestions/orders` → order `3149` |
| Draft create | `POST /content-calendar` → `entry_id=3` |
| Pending approval | `PATCH` → `status: pending_approval` |
| Telegram alert | `_notify_pending_approval` — no TG error in logs |

Script: `deployment/deploy-b2-calendar-e2e.sh` → **PASS** on VPS

---

## Delivered (Phase B.3 — INT-011 Facebook publish)

| Item | Path / proof |
|------|----------------|
| Publisher | `agent/publishers/facebook.py` (Graph v25) |
| Schema | `publish_result`, `media_url`, `fb_post_id`, `scheduled_publish_at` |
| Node | `publish_entry()`, `publish_due_scheduled_entries()` |
| API | `POST/GET …/content-calendar/{id}/publish` |
| Worker | `FB_PUBLISH_CHECK_INTERVAL_SECONDS` in `api/app.py` |
| VPS E2E | `deployment/deploy-b3-fb-publish-e2e.sh` → entry_id=7, fb_post_id=491325420727745_122179053746613375 |

Handoffs: `docs/handoffs/2026-06-30-b3-fb-publish-implementation.md`, `docs/handoffs/2026-07-01-b3-fb-publish-e2e.md`

---

## Deferred (not in Phase B scope)

| Item | Reason |
|------|--------|
| B3.1 FB insights reader | Dowódca — revisit later |
| B3.2 FB comments read | Dowódca — revisit later |
| B3.3 FB reply HITL | Dowódca — revisit later |
| TikTok publish (Phase C) | Charter — post-angel |
| GA4 snapshot persist | Optional follow-up (COI synthesis) |

---

## Regression

```bash
pytest tests/ -q
curl -H "Authorization: Bearer $JWT" http://localhost:8000/api/v1/content-calendar
```
