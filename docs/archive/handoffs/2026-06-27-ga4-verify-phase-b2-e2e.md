# Handoff — GA4 zzpackage verify + Phase B.2 calendar E2E

**Date:** 2026-06-27  
**Branch:** `master` @ `901ebcc` (local uncommitted)  
**Plan:** `docs/plans/PLAN-COI-PHASE-B.md`

---

## TASK_CLASSIFICATION

**Feature** (verification + E2E proof; kod P2-01/P2-02 już na VPS)

---

## DONE

### 1. GA4 zzpackage verify — PASS

| Step | Result |
|------|--------|
| `systemctl restart jadzia` | OK (cache TTL reset) |
| `GET /api/v1/analytics/snapshot?period=7d` | `sync_status: success` |
| `sources.zzpackage` | present (`sessions: 23`) |
| `errors` | `[]` |

Proof script: `deployment/verify-ga4-zzpackage.sh`  
Updated: `docs/handoffs/2026-06-26-deploy-int-009-proof.md`

### 2. Phase B.2 E2E workflow — PASS

```text
order 3149 → GET /content-calendar/suggestions/orders
→ POST draft (entry_id=3, source_order_id=3149)
→ PATCH pending_approval → Telegram alert (async)
```

| Step | HTTP | Detail |
|------|------|--------|
| Suggestions | 200 | 2 orders (3149 + SMOKE-1) |
| POST draft | 200 | `sync_status: success`, `entry_id: 3` |
| PATCH status | 200 | `status: pending_approval` |

Proof script: `deployment/deploy-b2-calendar-e2e.sh`  
Local tests: 10 passed (`test_content_calendar_*`, `test_calendar_store`)

### 3. Docs / backlog

- `PLAN-COI-PHASE-B.md` — B.2 E2E marked done; next = B.3 (FB/TikTok API)
- `todo.json` — P2-03 added/completed; DEPLOY-03 note updated

---

## LEFT (Dowódca / next agent)

| Item | Owner | Note |
|------|-------|------|
| Telegram delivery confirm | Dowódca | Alert fired async for entry_id=3 — potwierdź wiadomość w TG |
| Phase B.3 FB/TikTok API | agent | Dep audit + publish integration |
| Mollie UI checkout | Dowódca | Optional revenue video proof |
| OPS-01 VPS user `jadzia` | Dowódca | Repo ready; VPS still root |

---

## RISKS

| Risk | Status |
|------|--------|
| GA4 zzpackage PermissionDenied | **Resolved** — SA Viewer on 528785553 |
| Telegram alert silent fail | Low — no TG error in logs; Dowódca confirm |
| CRLF in bash scripts from Windows | Fixed before upload; use LF in repo |

---

## V-FILES

```
jadzia-core/todo.json
jadzia-core/docs/plans/PLAN-COI-PHASE-B.md
jadzia-core/docs/handoffs/2026-06-26-deploy-int-009-proof.md
jadzia-core/deployment/deploy-b2-calendar-e2e.sh
jadzia-core/deployment/verify-ga4-zzpackage.sh
```

---

## Uncommitted (jadzia-core)

- `deployment/verify-ga4-zzpackage.sh` (new)
- `deployment/deploy-b2-calendar-e2e.sh` (new)
- `docs/handoffs/2026-06-27-ga4-verify-phase-b2-e2e.md` (this file)
- `docs/handoffs/2026-06-26-deploy-int-009-proof.md` (updated)
- `docs/plans/PLAN-COI-PHASE-B.md` (updated)
- `todo.json` (updated)
- Pre-existing: `docs/handoffs/2026-06-26-coi-docs-alignment.md`

---

RECOMMENDED_NEXT: Dowódca confirm TG alert → Phase B.3 FB/TikTok API audit  
WHY_NEXT: B.2 E2E closed; publish API is next plan milestone
