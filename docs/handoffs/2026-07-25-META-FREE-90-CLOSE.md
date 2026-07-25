# Handoff — META-FREE-90 (PARTIAL GATE)

**Date:** 2026-07-25  
**Status:** **8/10 LIVE** @ tip **`d004900`** — agent F0–F3 + S6/S10 done · **S5+S9 ready_for_human**  
**standing_go_closeout:** `false`  
**Kampanie Ads:** HOLD (do ≥9/10 + osobne GO)

## Deploy VERIFY

| Check | Result |
|-------|--------|
| git tip VPS | `d004900` |
| `jadzia` | active |
| fb-health | PAGE · `has_read_insights` · `has_pages_read_user_content` · Token OK |
| live post metrics | ok · impressions 239 · insights_ok |
| `organic_er_baseline_30d` | numeric 0.0 |
| redact | REDACT_OK |
| parks | `l0_purchase`, `ads_api_create` only |

## Score

| PASS | FAIL (HITL) |
|------|-------------|
| S1 S2 S3 S4 S6 S7 S8 S10 | S5 Messenger Away/menu · S9 IG Pro dual |

## Co zrobione (evidence, no secrets)

### F0
- SoT [FREE-META-90.md](../ops/marketing/FREE-META-90.md) · OPERATOR · todo

### F1 (LIVE VPS)
- App permission `pages_read_user_content` → Ready for testing  
- OAuth rerequest + `set-fb-access-token.py` → PAGE `expires_at=0`  
- `fb-health`: `has_pages_read_user_content=true` · `has_read_insights=true` · `Token OK (Page)`  
- Metrics Graph v25: `post_media_view` + `post_total_media_view_unique` + `post_clicks`  
- Redact `access_token` in publisher logs  
- DTL: `organic_er_baseline_30d` numeric (0.0) · conscious park `fb_pages_read_user_content` gone when scope present  
- Code files on VPS: `facebook.py`, `facebook_organic.py`, `report.py` (deployed via scp; tip-sync commit recommended)

### F2 (partial)
- **S6 PASS:** Page FlexGrafik shows **Wyślij wiadomość**  
- **S5 FAIL:** Automated responses UI not set (needs Dowódca ~10 min)

### F3
- Cancelled smoke drafts (12 entries)  
- Published 2 NL business posts with Wizard `utm_medium=organic`  
- Published 1 video (Drive) with `utm_content=reel_a` · calendar entry 26  

### F4
- IG not linked (BS CTA **Powiąż z kontem na Instagramie**) → park

### F5
- S10 exercise note: 2026-07-25T06:15Z — proces SPEED-TO-LEAD przećwiczony dokumentacyjnie (brak live organic lead w sesji); przy następnym DM/komentarzu: WA/Messenger &lt;15 min wg [SPEED-TO-LEAD.md](../ops/marketing/SPEED-TO-LEAD.md)

## Hard STOP held

No Ads create · no Mollie · no secrets in git

## NEXT (1-1-1)

1. **Dowódca:** S5 Away+menu **albo** S9 IG → score ≥9/10  
2. Agent: tip-sync commit kodu F1 gdy GO · re-dogfood Commander ER  
3. Potem dopiero kampanie (`META-CLICK-PATH`)
