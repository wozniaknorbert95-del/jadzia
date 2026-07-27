---
status: "[ACTIVE]"
title: "FREE-TIKTOK — Jadzia channel (system first)"
updated: "2026-07-26 (TT-PUB-01 wiring · no ad-hoc Studio post)"
gate: "FREE-TIKTOK / TT-PUB-01"
---

# FREE-TIKTOK — SoT (system)

**Cel:** TikTok `@flexgrafik.nl` zarządzany przez **Jadzia jak FB** — calendar → approve → publisher → DTL.  
**Nie cel:** ręczny Studio post „żeby zaliczyć scorecard” bez ścieżki w kodzie.

**Design:** [2026-07-26-free-tiktok-jadzia-channel-design.md](../../superpowers/specs/2026-07-26-free-tiktok-jadzia-channel-design.md)  
**Plan:** [2026-07-26-FREE-TIKTOK-PLAN.md](../../handoffs/2026-07-26-FREE-TIKTOK-PLAN.md)  
**GTM:** [GTM-1PAGER.md](./GTM-1PAGER.md) — kanał **#2** po Meta final + asset cadence · KPI = `wizard_starts` utm=tiktok.

**Instagram:** out of scope.

---

## Kierunek (korekta 2026-07-26)

| Źle | Dobrze |
|-----|--------|
| Agent publikuje w przeglądarce Studio bez planu | `agent/publishers/tiktok.py` + calendar `platform=tiktok` |
| Gate = „wrzuć 1 clip ręcznie” | Gate = **system ready** + 1 dowód publish przez Commander/API |
| Scraper / RPA DM / 4-agent circus | PARK / HARD STOP |

---

## Scorecard systemu (TT-PUB)

| # | Kryterium | Status | Evidence |
|---|-----------|--------|----------|
| S1 | `tiktok.py` Direct Post PULL_FROM_URL + redact | **PASS** | `agent/publishers/tiktok.py` |
| S2 | `calendar_publish` routes `platform=tiktok` + video only | **PASS** | `calendar_publish.py` |
| S3 | Commander / content_calendar_node publish TT | **PASS** | `commander/publish.py` · `content_calendar_node.py` |
| S4 | DB `tiktok_post_id` + `.env.example` `TIKTOK_*` | **PASS** | `db.py` · `.env.example` |
| S5 | Unit tests mock API | **PASS** | `tests/unit/test_tiktok_publisher.py` |
| S6 | VPS: `TIKTOK_ACCESS_TOKEN` + verified media URL domain | **FAIL** | HITL Developer app + GO deploy |
| S7 | E2E: 1 calendar entry `tiktok`/`video` → published | **FAIL** | po S6 |

**Score LIVE:** **5/7** (kod) · prod live publish = S6+S7.

---

## Flow (jak FB)

```
POST /api/v1/content-calendar  platform=tiktok content_type=video media_url=https://…
  → status approved (HITL)
POST /api/v1/content-calendar/{id}/publish   (lub worker due)
  → tiktok.publish_video(title=body_nl, video_url=media_url)
  → tiktok_post_id = publish_id
```

Env (VPS only): `TIKTOK_ACCESS_TOKEN` · optional `TIKTOK_OPEN_ID` · `TIKTOK_DEFAULT_PRIVACY`.

**Wymagania TikTok Dev (HITL):** app z Content Posting · scope `video.publish` · verified URL prefix dla hosta `media_url`.

---

## Ops leftover (po S7 — nie blokuje kodu)

- Caption NL + first-comment UTM Wizard (Studio lub API comment later).  
- Cadence 2–3/tydz.  
- TT-INS-01 metrics → DTL · TT-CMT-01 comments.

## Hard STOP

RPA DM · secrets w repo · fake PASS · Ads Meta bez **„final”** · deploy bez GO · scrape trends stack.
