# Handoff CLOSE — OPS-FB-TOKEN-01 (LIVE)

**Date:** 2026-07-25  
**Status:** **LIVE** (VPS `.env` Page token + `read_insights`)  
**Code tip:** `58ffd1d` (no code change required)  
**standing_go_closeout:** `false` (GO = this session plan accept)

## Evidence (no secrets)

| Check | Result |
|-------|--------|
| App permission | `read_insights` added to PAGES_API use case → Ready for testing |
| OAuth | User re-auth with scopes incl. insights + Page FlexGrafik |
| `set-fb-access-token.py` | long-lived USER → PAGE exchange **success** |
| `fb-health` | `ok=true` · `token_type=PAGE` · **`has_read_insights=true`** · `message_pl=Token OK (Page)` · `expires_at=0` |
| Data Health parks | `fb_read_insights` **gone** · remain: `l0_purchase`, `ads_api_create` |
| Dogfood Start | `Ops: OK` · SLA **0** · Freshness/GA4 **ok** · **no** „Token Facebook wygasł” |
| Stale queue | cancelled calendar `entry_id=6` (B3 debug2 publish_failed; root cause OAuth 190 — humanize mapped to „wygasł”) |

URL: https://api.zzpackage.flexgrafik.nl/commander/?v=mkt-dash08

## Hard STOP held

- No Ads campaigns created/edited  
- No hot_lead Confirm · no organic publish in dogfood  
- No secrets / token in git or handoff body  

## LEFT

| Item | Owner |
|------|-------|
| Meta HOLD / Ads campaigns | human — later (`META-CLICK-PATH`) |
| Mollie / L0 Purchase | human |
| Optional: humanize OAuth 190 „Application deleted” vs expired | agent Low |

## NEXT

Observe Marketing organic + DTL facebook_organic. Campaigns only when Dowódca says final.
