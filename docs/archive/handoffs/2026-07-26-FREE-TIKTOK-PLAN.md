---
status: "[ACTIVE]"
title: "FREE-TIKTOK — plan SYSTEM (TT-PUB-01)"
updated: "2026-07-26"
gate: "TT-PUB-01"
---

# FREE-TIKTOK — plan działania (system)

## Korekta kierunku

**Nie:** ręczna publikacja w TikTok Studio „żeby domknąć 3/3”.  
**Tak:** wdrożenie kanału w Jadzia **jak FB** — publisher + calendar + Commander.

## Done (kod)

- `agent/publishers/tiktok.py` — Content Posting Direct Post / PULL_FROM_URL  
- `calendar_publish.py` — `platform=tiktok` → video only  
- `commander/publish.py` + `content_calendar_node.py` — TT branch + due worker  
- DB `tiktok_post_id` · `.env.example` `TIKTOK_*`  
- `tests/unit/test_tiktok_publisher.py`

## Next (HITL + GO)

1. TikTok Developer app → OAuth `video.publish` → `TIKTOK_ACCESS_TOKEN` na VPS (nie w git).  
2. Verify URL prefix dla hosta `media_url` (HTTPS, no redirect).  
3. GO deploy tip z TT-PUB.  
4. E2E: calendar entry `tiktok`/`video` → publish → `tiktok_post_id`.  
5. Potem ops: UTM first-comment / cadence · TT-INS-01 · TT-CMT-01.

## Hard STOP

RPA DM · browser-only fake PASS · secrets · deploy bez GO.
