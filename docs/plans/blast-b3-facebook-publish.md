# BLAST ANCHOR: B.3 - Facebook Content Publishing

**Task:** B.3 - FB publish integration + scheduled publish
**Type:** FEATURE
**INT:** INT-011 (new) - Jadzia to Facebook Graph API publish
**Parent:** PLAN-COI-PHASE-B.md

## Problem

content_calendar_node has flow draft -> pending_approval -> approved -> published but is missing the ACTUAL publish engine. Entries with status="approved" stay in DB without publishing to Facebook.

## Contract

When a calendar entry reaches `approved` status, Jadzia publishes it to Facebook via Graph API and records the result.

## Scope

### IN scope
1. **Schema migration** - add `publish_result` (JSON) + `media_url` (TEXT) + `fb_post_id` (TEXT) + `scheduled_publish_at` (TEXT) to content_calendar table
2. **Facebook publisher module** - `agent/publishers/facebook.py` with:
   - `publish_post(message, scheduled_time)` - POST /{page_id}/feed
   - `check_post_status(post_id)` - GET /{post_id}
3. **content_calendar_node update** - add `publish_entry(entry_id)` method
4. **New API endpoints**:
   - POST `/api/v1/content-calendar/{entry_id}/publish` - manual trigger
   - GET `/api/v1/content-calendar/{entry_id}/publish-status` - check FB result
5. **Worker loop integration** - worker checks for scheduled entries and publishes at scheduled time
6. **Tests** - unit tests for facebook publisher, integration tests for new endpoints

### OUT of scope
- TikTok publish (deferred to Phase C)
- Instagram publish
- Media upload to Facebook (photo/video)
- OAuth2 token refresh automation
- Multi-platform publish

## Required changes

### 1. agent/publishers/facebook.py (NEW)

```python
"""Facebook Graph API publisher - INT-011."""

import os
from typing import Optional
import requests

FACEBOOK_API_VERSION = "v19.0"
FACEBOOK_BASE = f"https://graph.facebook.com/{FACEBOOK_API_VERSION}"


def _get_config():
    page_id = os.getenv("FB_PAGE_ID")
    access_token = os.getenv("FB_ACCESS_TOKEN")
    if not page_id or not access_token:
        raise RuntimeError("FB_PAGE_ID and FB_ACCESS_TOKEN required in .env")
    return page_id, access_token


def publish_post(message: str, scheduled_publish_time: Optional[int] = None) -> dict:
    """Publish a text post to Facebook Page.
    
    Args:
        message: Post text content
        scheduled_publish_time: Unix timestamp for scheduled publish
    
    Returns:
        dict with post_id, status, and error (if any)
    """
    page_id, access_token = _get_config()
    url = f"{FACEBOOK_BASE}/{page_id}/feed"

    payload = {
        "message": message,
        "access_token": access_token,
    }
    
    if scheduled_publish_time:
        payload["published"] = "false"
        payload["scheduled_publish_time"] = scheduled_publish_time

    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return {
            "status": "success",
            "post_id": data.get("id"),
            "scheduled": bool(scheduled_publish_time),
        }
    except requests.RequestException as e:
        return {
            "status": "error",
            "error": str(e),
            "details": getattr(resp, "text", None),
        }


def check_post_status(post_id: str) -> dict:
    """Check if a scheduled/queued post is ready."""
    _, access_token = _get_config()
    url = f"{FACEBOOK_BASE}/{post_id}"
    
    try:
        resp = requests.get(
            url,
            params={"access_token": access_token, "fields": "status,message,created_time"},
            timeout=15
        )
        resp.raise_for_status()
        return {"status": "success", "data": resp.json()}
    except requests.RequestException as e:
        return {"status": "error", "error": str(e)}
```

### 2. agent/db.py - migrate content_calendar table

Add columns in `_create_tables()`:
```sql
ALTER TABLE content_calendar ADD COLUMN IF NOT EXISTS publish_result TEXT;
ALTER TABLE content_calendar ADD COLUMN IF NOT EXISTS media_url TEXT;
ALTER TABLE content_calendar ADD COLUMN IF NOT EXISTS fb_post_id TEXT;
ALTER TABLE content_calendar ADD COLUMN IF NOT EXISTS scheduled_publish_at TEXT;
```

Update `db_update_calendar_entry()` to handle new fields.

### 3. agent/nodes/content_calendar_node.py

Add method:
```python
def publish_entry(entry_id: str) -> dict:
    """Publish an approved entry to Facebook."""
    from agent.db import db_get_calendar_entry, db_update_calendar_entry
    from agent.publishers.facebook import publish_post
    import json

    row = db_get_calendar_entry(int(entry_id))
    if not row:
        return {"status": "error", "message": "Entry not found"}
    if row["status"] != "approved":
        return {"status": "error", "message": f"Entry must be approved, not {row['status']}"}
    
    result = publish_post(row["body_nl"])
    
    db_update_calendar_entry(int(entry_id), {
        "status": "published" if result["status"] == "success" else "failed",
        "fb_post_id": result.get("post_id"),
        "publish_result": json.dumps(result),
    })
    
    return result
```

### 4. api/routes/content_calendar.py

Add routes:
```python
@router.post("/api/v1/content-calendar/{entry_id}/publish")
async def publish_entry_endpoint(
    entry_id: str,
    _auth = Depends(verify_jwt),
):
    from agent.nodes.content_calendar_node import publish_entry
    result = publish_entry(entry_id)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result)
    return result


@router.get("/api/v1/content-calendar/{entry_id}/publish-status")
async def get_publish_status(
    entry_id: str,
    _auth = Depends(verify_jwt),
):
    from agent.db import db_get_calendar_entry
    row = db_get_calendar_entry(int(entry_id))
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return {
        "entry_id": entry_id,
        "status": row["status"],
        "fb_post_id": row.get("fb_post_id"),
        "publish_result": row.get("publish_result"),
    }
```

### 5. Worker loop - scheduled publish

Add to worker loop (every 60s):
```python
from agent.nodes.content_calendar_node import publish_entry
from agent.db import db_list_calendar_entries
from datetime import datetime, timezone

entries = db_list_calendar_entries(status="approved", limit=50)
for entry in entries:
    sched = entry.get("scheduled_publish_at")
    if sched:
        sched_dt = datetime.fromisoformat(sched)
        if sched_dt <= datetime.now(timezone.utc):
            publish_entry(str(entry["entry_id"]))
```

## Dependencies

- `requests` (check if in requirements.txt)
- .env: FB_PAGE_ID, FB_ACCESS_TOKEN
- Facebook App with Pages:manage_posts permission

## Test plan

1. Unit: test facebook publisher with mock responses (success, error)
2. Unit: test approve to published flow (mock FB call)
3. Integration: POST /publish with mock JWT
4. Integration: GET /publish-status
5. Regression: all 342 existing tests still pass

## BLAST CHECKLIST

- [ ] agent/publishers/__init__.py (NEW)
- [ ] agent/publishers/facebook.py (NEW)
- [ ] agent/db.py - add 4 columns to schema
- [ ] agent/nodes/content_calendar_node.py - publish_entry()
- [ ] core/models.py - new request/response models if needed
- [ ] api/routes/content_calendar.py - 2 new endpoints
- [ ] worker loop - scheduled publish check (api/app.py)
- [ ] tests/test_facebook_publisher.py (NEW)
- [ ] tests/unit/test_facebook_publish.py (NEW)
- [ ] .env.example - document FB_PAGE_ID, FB_ACCESS_TOKEN
