# Handoff — B3 Facebook Publish implementation (INT-011)

**Date:** 2026-06-30  
**Task:** B3-01 through B3-06 — Facebook Graph API publish engine  
**Status:** CODE COMPLETE — VPS E2E pending (Zasada 11)

## Summary

Implemented INT-011 Facebook Page publish for approved `content_calendar` entries. Token obtained for FlexGrafik page (`491325420727745`); must be placed on VPS only — **never commit or paste in handoffs**.

## Delivered

| Item | Path |
|------|------|
| Publisher module | `agent/publishers/facebook.py` (Graph v25.0) |
| Schema columns | `publish_result`, `media_url`, `fb_post_id`, `scheduled_publish_at` |
| Node | `publish_entry()`, `publish_due_scheduled_entries()` |
| API | `POST /api/v1/content-calendar/{id}/publish` |
| API | `GET /api/v1/content-calendar/{id}/publish-status` |
| Worker | `FB_PUBLISH_CHECK_INTERVAL_SECONDS` (default 60) |
| Tests | `test_facebook_publisher.py`, `test_facebook_publish.py` + API flow |
| Env template | `.env.example` |
| E2E script | `deployment/deploy-b3-fb-publish-e2e.sh` |

## Verification (local)

```
pytest tests/ -q  → 359 passed, 1 skipped, 1 xfailed
```

## VPS deploy checklist (Dowódca)

1. Backup DB on VPS:
   ```bash
   sqlite3 /opt/jadzia/data/jadzia.db ".backup /opt/jadzia/backups/pre-b3-$(date +%Y%m%d-%H%M%S).db"
   ```
2. Deploy code to `/opt/jadzia` (exclude `data/`, `.env`, `venv/`)
3. Append to `/opt/jadzia/.env` (chmod 600):
   ```
   FB_PAGE_ID=491325420727745
   FB_ACCESS_TOKEN=<Page Access Token — secure channel only>
   FB_PUBLISH_CHECK_INTERVAL_SECONDS=60
   ```
4. `pip install -r requirements.txt && sudo systemctl restart jadzia`
5. `bash /opt/jadzia/deployment/prod-smoke.sh`
6. E2E test post:
   ```bash
   bash /opt/jadzia/deployment/deploy-b3-fb-publish-e2e.sh
   ```
7. Verify post on Facebook page FlexGrafik; delete test post manually
8. **Rotate FB token** (was exposed in chat during setup)

## Security

- Token from chat is compromised — rotate after first successful E2E
- Prefer long-lived Page Token exchange on VPS (App Secret never in repo/chat)
- gitleaks: no secrets in committed files

## Roadmap (next sessions)

| ID | Capability | Meta permissions |
|----|------------|------------------|
| B3.1 | Page insights + post list | `pages_read_engagement`, `read_insights` |
| B3.2 | Read comments → Telegram brief | `pages_read_user_content` |
| B3.3 | Reply to comments (HITL) | `pages_manage_engagement` |
| B3.4 | Webhooks for new comments | `pages_manage_metadata` |

## Next

- **Human:** B3-DEPLOY — run checklist above
- **Agent:** B3.1 insights reader after E2E proof
