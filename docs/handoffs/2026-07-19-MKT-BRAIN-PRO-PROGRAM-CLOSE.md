# Handoff — MKT-BRAIN-PRO PROGRAM CLOSE

**Date:** 2026-07-19  
**Gate:** MKT-BRAIN-PRO  
**Status:** Agent-only debt CLOSED · overall **~86%** · tip **`3c2fc6e`**  
**MB_MODE:** `propose`

## Co agent domknął (Stage 1–2)

### Stage 1 — INSIGHTS-READY

- `check_token_health()` → `scopes[]`, `has_read_insights`, `message_pl`
- Organic reason codes: `insights_scope_missing` | `no_published_posts` | `proxy_er` | `ok`
- Data Health: freshness `facebook_organic` + conscious park `fb_read_insights` (info, nie psuje overall)
- Docs: `FB-TOKEN-ROTATION.md` includes `read_insights`
- Pytest: token health + organic reason + report park

**VPS evidence (`3c2fc6e`):**
```
fb_ok True has_read_insights False
scopes ['pages_manage_posts', 'pages_read_engagement', 'pages_show_list', 'public_profile']
msg … brak scope read_insights …
```
→ agent-half READY; LIVE organic insights po Graph re-auth (H-Insights).

### Stage 2 — WEEKLY-DRAFT

- `agent/marketing/weekly_scorecard.py` — draft z DTL (leads/orders/margin/attr/organic)
- CLI `scripts/mb_weekly_scorecard_draft.py` · `GET …/marketing/weekly-draft`
- TG weekly nudge (`MARKETING_WEEKLY_SCORECARD_INTERVAL_SECONDS=604800`) — **bez** HOLD/KILL
- Spend/CPL = `null` + nota Ads Manager

**VPS evidence:**
```
week 2026-W29 leads 7.0 spend None cpl None decision None
```

## Progress (board SoT)

| Warstwa | % |
|---------|---|
| Runtime F0→F4b | **100%** |
| Data Health honesty | **~98%** |
| Insights agent-half (#5) | **READY** (LIVE po Graph) |
| Weekly scorecard draft | **LIVE** |
| Paid Meta ops (#1) | **70%** HOLD €5 |
| L0 pixel | **50%** IC PASS / Purchase PARK |
| F4 extras | **0%** ready_for_human |
| **Overall** | **~86%** |

**Cap bez HITL:** Meta HOLD · Purchase · Graph `read_insights` · F4 extras.

## ready_for_human (freeze — nie „later”)

| ID | Checklist Dowódcy |
|----|-------------------|
| H-Meta | Hold 7d ad set €5; potem optimize — [META-CLICK-PATH](../ops/marketing/META-CLICK-PATH.md) |
| H-Purchase | Mollie GO → Test Events Purchase |
| H-Insights | Graph: `read_insights` → nowy `FB_TOKEN` → `set-fb-access-token` |
| H-WA | Lead → WA &lt;15 min — [SPEED-TO-LEAD](../ops/marketing/SPEED-TO-LEAD.md) |
| H-F4x | Distribution / blog / lead webhook — dopiero po triggerach (leady / GO) |

## Next

- **Agent:** observe-only propose cycles · no Ads create · no Mollie
- **Human:** 5 punktów checklisty powyżej
- **Zakaz:** reorder #1 Meta · fake PASS · deploy bez GO

## Hard PARK (poza sesją)

Gate D · Mollie LIVE charge · Ads API create · TikTok API · full auto-publish · MMM · Redis
