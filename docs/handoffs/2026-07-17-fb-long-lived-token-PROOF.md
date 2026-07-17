# Handoff — FB long-lived Page Token + publish smoke

**Date:** 2026-07-17  
**VPS:** `/opt/jadzia` @ `4186387`+ (set-fb reload fix applied on disk)  
**Gate:** `FB-TOKEN-ROTATION` → **CLOSED**

---

## DONE

| Step | Result |
|------|--------|
| `FB_APP_ID` / `FB_APP_SECRET` on VPS | SET (not in git) |
| Long-lived exchange | success (`expires_in` ~60d USER intermediate) |
| Page token | **PAGE**, `is_valid: true`, **`expires_at: 0`** (never expires) |
| Scopes | `pages_manage_posts`, `pages_read_engagement`, `pages_show_list` |
| Text publish smoke | PASS `post_id=491325420727745_122180368724613375` |
| Photo publish smoke | PASS `post_id=491325420727745_122180368784613375` |
| M2 MIME gate | PASS |
| M2 Graph video (sample GCS URL) | FAIL — Meta `Unable to fetch video file from URL` (not token) |

---

## Bugfix (same session)

`set-fb-access-token.py` after USER→PAGE subprocess still had old USER in `os.environ`. Fixed: `_load_env_into_os()` before final `check_token_health()`.

---

## LEFT

| Item | Owner |
|------|-------|
| M2 video E2E with **real GDrive MP4** (`M2_TEST_GDRIVE_URL`) | Dowódca paste link + agent retry |
| Optional: rotate App Secret (was pasted in chat) | human hygiene |
| Commit set-fb reload fix + apply helpers to origin | agent (this handoff commit) |

---

## Verify anytime

```bash
cd /opt/jadzia
venv/bin/python deployment/inspect-fb-token.py
# type PAGE, expires_at 0, is_valid true
```

Commander → Marketing → „Facebook: Token OK (Page)”.

---

```
SESSION_VERDICT: SUCCESS (token forever-ish)
M2_VIDEO_E2E: needs public Drive MP4 URL (token OK)
```
