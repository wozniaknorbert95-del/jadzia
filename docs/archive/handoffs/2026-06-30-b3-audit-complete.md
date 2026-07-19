# Handoff: B.3 — Facebook Content Publishing Audit + Blast Contract

**Date:** 2026-06-30
**Task:** B.3 - FB/TikTok publish API audit + blast contract
**Status:** AUDIT COMPLETE, CONTRACT READY
**Next:** /implement (B3-01 through B3-06)

## Audit Results

### Facebook Graph API
- **Status:** READY for implementation
- **Auth:** Page Access Token (simple, no OAuth complexity)
- **Endpoint:** POST /{page_id}/feed
- **Content:** Text + image supported natively
- **Scheduling:** Native API support (scheduled_publish_time)
- **Cost:** FREE (requires FB Developer account + Page access)
- **Token expiry:** 60 days (extendable)
- **Rate limit:** 200 calls/hour/page

### TikTok for Business API
- **Status:** DEFERRED to Phase C
- **Reason:** Video-only, requires TikTok Developer Program approval
- **Complexity:** Higher setup barrier than FB

## Blast Contract

`docs/plans/blast-b3-facebook-publish.md` created with:
- Full technical contract for INT-011
- Required changes: 6 files + tests
- 2 new API endpoints: POST /publish, GET /publish-status
- Schema additions: 4 new columns to content_calendar
- Worker loop integration for scheduled publish
- Test plan with 5 verification steps

## Dependencies

Before implementation:
1. **Commander action required:** Create Facebook App + get Page Access Token
2. **Config needed:** FB_PAGE_ID and FB_ACCESS_TOKEN in .env

## Next tasks (B.3 implementation order)

1. **B3-01:** agent/publishers/facebook.py (NEW module)
2. **B3-02:** Schema migration (4 new columns)
3. **B3-03:** content_calendar_node: publish_entry()
4. **B3-04:** API endpoints (publish, status)
5. **B3-05:** Worker loop scheduled publish
6. **B3-06:** Tests (unit + integration)

## todo.json updated

- B3-01 through B3-06 added
- C1-01 (TikTok deferred) added
- next_agent set to B3-01
