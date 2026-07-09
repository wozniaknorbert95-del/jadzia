# COI Content Intake M1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dowódca dodaje posty FB (tekst + grafika z linku Google Drive) w Commander Marketing, ustawia harmonogram, system publikuje o czasie.

**Architecture:** Zewnętrzne media URL (GDrive) → `agent/media/gdrive.py` normalizacja + probe → `content_calendar` SQLite → worker `publish_due_scheduled_entries` → `facebook.publish_photo` / `publish_post`. Zero uploadu na VPS.

**Tech Stack:** FastAPI, SQLite, vanilla JS Commander UI, Facebook Graph API v25, httpx probe.

**Spec:** [`docs/superpowers/specs/2026-07-09-coi-content-intake-design.md`](../specs/2026-07-09-coi-content-intake-design.md) — **APPROVED**

**GDrive setup:** [`docs/ops/COI-MARKETING-GDRIVE-SETUP.md`](../../ops/COI-MARKETING-GDRIVE-SETUP.md)

---

## File map

| File | Responsibility |
|------|----------------|
| `agent/media/gdrive.py` | URL parse, normalize, probe ✅ (foundation) |
| `agent/db.py` | `content_type`, `media_source` columns |
| `core/models.py` | Create/Update request fields |
| `agent/publishers/facebook.py` | `publish_photo(message, image_url)` |
| `agent/nodes/content_calendar_node.py` | Route publish by `content_type` |
| `agent/commander/publish.py` | Use photo path when media present |
| `api/routes/content_calendar.py` | Validate media on create/patch |
| `commander-ui/app.js` + `index.html` | Composer + queue |
| `tests/unit/test_gdrive.py` | ✅ |
| `tests/unit/test_content_calendar_media.py` | API + publish routing |

---

### Task 1: Schema — content_type + media_source

**Files:**
- Modify: `agent/db.py` (migration list ~line 326)
- Modify: `core/models.py` ContentCalendarCreateRequest, Update, Entry

- [ ] **Step 1: Add columns in db migration**

```python
# agent/db.py _CALENDAR_MIGRATIONS or equivalent tuple
("content_type", "TEXT DEFAULT 'text'"),
("media_source", "TEXT"),
```

- [ ] **Step 2: Extend models**

```python
# core/models.py
content_type: Literal["text", "image", "video"] = "text"
media_url: Optional[str] = None
scheduled_publish_at: Optional[str] = None
media_source: Optional[Literal["gdrive", "external"]] = None
```

Add same optional fields to `ContentCalendarCreateRequest` and `ContentCalendarUpdateRequest`.

- [ ] **Step 3: Update db_create_calendar_entry / db_update allowed fields**

- [ ] **Step 4: Run tests** `pytest tests/unit/test_content_calendar_api.py -q`

- [ ] **Step 5: Commit** `feat(content-intake): schema content_type media_source`

---

### Task 2: API — create with GDrive normalize + probe

**Files:**
- Modify: `api/routes/content_calendar.py`
- Modify: `agent/nodes/content_calendar_node.py` create_calendar_entry

- [ ] **Step 1: Write failing test**

```python
# tests/unit/test_content_calendar_media.py
def test_create_image_entry_normalizes_gdrive(client, temp_db):
    body = {
        "platform": "facebook",
        "title": "Test post",
        "body_nl": "NL caption hier",
        "scheduled_at": "2026-07-15T09:00:00+00:00",
        "content_type": "image",
        "media_url": "https://drive.google.com/file/d/abc123/view",
        "scheduled_publish_at": "2026-07-15T09:00:00+00:00",
    }
    r = client.post("/api/v1/content-calendar", json=body, headers=auth)
    assert r.status_code == 200
    listed = client.get("/api/v1/content-calendar", headers=auth).json()
    entry = listed["entries"][0]
    assert "uc?export=download&id=abc123" in entry["media_url"]
```

- [ ] **Step 2: Implement in create_calendar_entry**

```python
from agent.media.gdrive import normalize_media_url, probe_media_url

if payload.content_type in ("image", "video") and payload.media_url:
    norm = normalize_media_url(payload.media_url)
    if not norm["ok"]:
        return ContentCalendarCreateResponse(entry_id="", sync_status="fail")
    probe = probe_media_url(norm["media_url"])
    # store norm fields; if not probe.ok and content_type==image: still allow draft with warning flag optional
```

- [ ] **Step 3: POST sets status draft by default; separate PATCH or combined "schedule" endpoint sets approved**

- [ ] **Step 4: pytest pass**

- [ ] **Step 5: Commit** `feat(content-intake): create calendar entry with gdrive media`

---

### Task 3: Facebook publish_photo

**Files:**
- Modify: `agent/publishers/facebook.py`
- Create: `tests/unit/test_facebook_photo.py`

- [ ] **Step 1: Failing test with requests mock**

```python
@patch("agent.publishers.facebook.requests.post")
def test_publish_photo_success(mock_post):
    mock_post.return_value.json.return_value = {"id": "photo_123"}
    mock_post.return_value.raise_for_status = lambda: None
    result = publish_photo("NL text", "https://drive.google.com/uc?export=download&id=x")
    assert result["status"] == "success"
```

- [ ] **Step 2: Implement**

```python
def publish_photo(message: str, image_url: str, scheduled_publish_time: Optional[int] = None) -> dict:
    page_id, access_token = _get_config()
    url = f"{FACEBOOK_BASE}/{page_id}/photos"
    payload = {"message": message, "url": image_url, "access_token": access_token}
    # scheduled if supported on photos endpoint
```

- [ ] **Step 3: Commit** `feat(content-intake): facebook publish_photo from URL`

---

### Task 4: Publish routing by content_type

**Files:**
- Modify: `agent/nodes/content_calendar_node.py` publish_entry
- Modify: `agent/commander/publish.py` publish_calendar_entry_system

- [ ] **Step 1: Test publish_entry calls publish_photo when content_type=image**

- [ ] **Step 2: Implement branch**

```python
if row.get("content_type") == "image" and row.get("media_url"):
    result = publish_photo(row["body_nl"], row["media_url"], sched_unix)
else:
    result = publish_post(row["body_nl"], sched_unix)
```

- [ ] **Step 3: Commit** `feat(content-intake): publish routing text vs image`

---

### Task 5: Commander UI — Composer + Queue

**Files:**
- Modify: `commander-ui/index.html` (composer form in view-marketing)
- Modify: `commander-ui/app.js` loadMarketing rewrite
- Modify: `commander-ui/styles.css` (composer panel)

- [ ] **Step 1: HTML — form fields**

```html
<form id="marketing-composer">
  <select id="content-type"><option value="text">Tekst</option><option value="image">Grafika + tekst</option></select>
  <input id="entry-title" placeholder="Tytuł (PL)" />
  <textarea id="entry-body" lang="nl" placeholder="Treść (NL)"></textarea>
  <input id="entry-media-url" type="url" placeholder="Link Google Drive (plik)" hidden />
  <input id="entry-schedule" type="datetime-local" />
  <button type="button" id="save-draft">Zapisz szkic</button>
  <button type="button" id="schedule-post">Zaplanuj publikację</button>
</form>
```

- [ ] **Step 2: JS — toggle media field on content type**

- [ ] **Step 3: JS — POST create + PATCH approved on Zaplanuj**

- [ ] **Step 4: JS — queue sorted by scheduled_publish_at, hide graduation/bulk**

- [ ] **Step 5: Settings — show marketing_gdrive_folder_url link if set**

- [ ] **Step 6: Manual test on localhost**

- [ ] **Step 7: Commit** `feat(content-intake): marketing composer UI`

---

### Task 6: Prod proof + handoff

**Files:**
- Create: `docs/handoffs/2026-07-XX-coi-content-intake-m1-PROOF.md`

- [ ] **Step 1: Dowódca creates COI-Marketing folder, sends link**

- [ ] **Step 2: Run set-marketing-gdrive-folder.py on VPS**

- [ ] **Step 3: Create test image entry, schedule + publish**

- [ ] **Step 4: Handoff with screenshot checklist**

- [ ] **Step 5: Commit handoff**

---

## Out of scope (M1)

- Video/Reels publish (M2)
- Google Drive OAuth API
- File upload to VPS
- TikTok platform

## Human gate before Task 6

Dowódca must provide folder URL:

```
https://drive.google.com/drive/folders/XXXXXXXX
```

---

## Self-review (plan vs spec)

| Spec requirement | Task |
|------------------|------|
| GDrive normalize | Task 1–2 ✅ |
| Probe on save | Task 2 |
| publish_photo | Task 3–4 |
| Composer UI | Task 5 |
| Solo operator flow draft→approved | Task 2, 5 |
| Playbook | Done (ops doc) |
| marketing_gdrive_folder settings | Task 1 settings ✅ + Task 5 UI |

**Gaps:** M2 video explicitly deferred. SMTP unrelated.

---

## Execution choice

After Dowódca provides GDrive folder link:

1. **Subagent-Driven** — one task per session  
2. **Inline** — full M1 in one long session  
