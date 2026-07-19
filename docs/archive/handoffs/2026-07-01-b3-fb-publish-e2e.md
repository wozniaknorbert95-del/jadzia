# Handoff — B3 Facebook Publish E2E PROOF

**Date:** 2026-07-01  
**Task:** B3-DEPLOY — VPS E2E INT-011  
**Status:** PASS

## Environment

- VPS: `185.243.54.115` — `/opt/jadzia`, user `jadzia`
- Page: **FlexGrafik** (`FB_PAGE_ID=491325420727745`)
- Graph API: v25.0

## E2E result

| Step | Result |
|------|--------|
| POST draft | entry_id=7 |
| PATCH approved | OK |
| POST publish | **200 success** |
| GET publish-status | status=published |

**fb_post_id:** `491325420727745_122179053746613375`

Test post text: `Jadzia COI test 20260701T0452xx — safe to delete` (remove manually on FB if still visible)

## Issues resolved during deploy

1. **Stale FB token** on VPS → updated Page Access Token (commander-provided)
2. **Meta error 190** initially: old token referenced deleted app
3. **`.env` permissions** after update → `chown jadzia:jadzia`, chmod 600
4. **`data/` ownership** after tar deploy → `chown -R jadzia:jadzia /opt/jadzia/data /opt/jadzia/logs`
5. **Shell CRLF** on VPS scripts → fix via `.gitattributes` `*.sh eol=lf`

## Security follow-up

- Token was exposed in chat — **rotate** in Graph API Explorer after confirming prod stable
- Exchange for **long-lived Page Token** on VPS (App Secret only on server)

## Next

- **B3.1:** Facebook insights reader
- Commit + push B3 code from local repo
