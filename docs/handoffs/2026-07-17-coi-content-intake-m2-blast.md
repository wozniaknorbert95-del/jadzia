# BLAST — COI-CONTENT-INTAKE-M2 (Video/Reels z GDrive)

**Date:** 2026-07-17  
**Backlog ID:** `COI-CONTENT-INTAKE-M2`  
**Spec:** `docs/superpowers/specs/2026-07-09-coi-content-intake-design.md` §M2  
**Branch:** `master` @ `1d46877`

---

## B — Background

Dowódca planuje posty wideo w Commander Marketing (link GDrive + caption NL). Worker publikuje o czasie przez Facebook Graph API — Meta pobiera plik z `file_url`. M1 dostarczył tekst + zdjęcie; `calendar_publish.py` zwraca stub error dla `content_type=video`.

**Flow:** UI → `POST /content-calendar` (probe video) → SQLite → worker → `publish_video` → Graph `POST /{page_id}/videos`.

---

## L — Limitations

- **No VPS file download** — tylko URL probe (HEAD), Meta fetchuje wideo.
- **GDrive large MP4** — virus-scan interstitial może failować; playbook R2 fallback (human).
- **Reels format** — poza scope; zwykły Page video post (`/videos`).
- **Timeout** — 120s na Graph video POST (większe pliki).
- **Zasada 11** — brak autonomicznego deploy.
- **Nie dotykać** `feat/da-insire-enterprise`.

---

## A — Implementation plan

- [x] `agent/publishers/facebook.py` — `publish_video(description, file_url)`
- [x] `agent/publishers/calendar_publish.py` — route `video` → `publish_video`
- [x] `agent/publishers/__init__.py` — export `publish_video`
- [x] `agent/nodes/content_calendar_node.py` — probe on create/update for `video`
- [x] `agent/publishers/facebook.py` — `parse_publish_error` video hints
- [x] `commander-ui/index.html` — enable Wideo option (remove M2 queue label)
- [x] `tests/unit/test_facebook_publisher.py` — video publish unit tests
- [x] `tests/unit/test_content_calendar_media.py` — video create + publish route
- [x] `tests/unit/test_calendar_publish.py` — routing unit tests

---

## S — Success criteria

- [ ] `pytest tests/unit/test_facebook_publisher.py tests/unit/test_content_calendar_media.py tests/unit/test_calendar_publish.py` PASS
- [ ] `ruff check` on touched files PASS
- [ ] `content_type=video` + GDrive URL → Graph `/videos` with `file_url`
- [ ] UI: „Wideo” bez „kolejka M2”
- [ ] Handoff + deploy checklist (manual approve)

---

## T — Test plan

| Layer | Test |
|-------|------|
| Unit | `publish_video` mock Graph — payload `description`, `file_url` |
| Unit | `publish_calendar_content` routes video row |
| API | create video entry normalizes GDrive + probe mock |
| Smoke | Dowódca: MP4 on Drive → Commander → publish (post-deploy) |

---

```
BLAST_ANCHOR: docs/handoffs/2026-07-17-coi-content-intake-m2-blast.md
BACKLOG_ID: COI-CONTENT-INTAKE-M2
INVARIANTS_TO_PROTECT: M1 text/image paths, worker loop, SQLite schema, no VPS upload
SUCCESS_CRITERIA: video publish end-to-end in code + tests green
IMPLEMENTATION_PLAN: facebook.publish_video → calendar_publish → node probe → UI → tests

---
CURRENT_STAGE: L1-Design → L2-Implement
RECOMMENDED_NEXT: /implement
WHY_NEXT: Contract established; M1 patterns reusable.
---
```
