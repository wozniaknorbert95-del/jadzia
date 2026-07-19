---
status: "[ACTIVE]"
title: "MKT-BRAIN-PRO — Organic DTL + CEO brief bridge CLOSE"
gate: "MKT-BRAIN-PRO-ORG-CEO"
updated: "2026-07-19"
result: "PASS local pytest — deploy pending tip"
---

# Organic FB DTL + CEO↔brief — CLOSE

## Done

| Item | Status |
|------|--------|
| `fetch_post_organic_metrics` (Graph, no Ads) | DONE |
| `ingest_facebook_organic_posts` → DTL facts + lift | DONE |
| Pipeline hook `facebook_organic` | DONE |
| Weekly brief → `publish_ceo_priority_stub` | DONE (`BRIEF_CEO_PRIORITY_ENABLED` default 1) |
| pytest `test_mb_organic_ceo.py` | PASS |

## Notes

- Without `read_insights`, ER uses engagement proxy + lower confidence; lift only when `quality_clean`.
- CEO bus uses `send_telegram=False` (brief already TG'd).
- **F4 / propose** still BLOCKED (14d shadow).
- Human: Meta pack, Purchase PARK, shadow eval-pack.

## Hard STOP

No Ads API create · no Mollie · no `MB_MODE=propose` without GO.
