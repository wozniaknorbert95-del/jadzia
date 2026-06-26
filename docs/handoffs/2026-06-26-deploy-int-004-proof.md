# DEPLOY-02 — INT-004 lead E2E proof

**Date:** 2026-06-26  
**Gate:** DEPLOY-02  
**Status:** PASS (server path verified)

## Checklist

- [x] `LEADS_API_KEY` set on jadzia VPS `.env`
- [x] zzpackage `wp-config.php`: `FG_JADZIA_LEADS_URL` + `FG_JADZIA_LEADS_API_KEY`
- [x] `fg-game-api.php` v1.3 deployed to zzpackage mu-plugins (`fg_jadzia_sync_lead`)
- [x] Direct `POST /api/v1/leads` → row in `leads` table
- [x] zzpackage `fg_jadzia_sync_lead()` → row in `leads` table
- [ ] Full browser game flow (Turnstile) — optional; server sync proven
- [ ] Duplicate email → `sync_status: duplicate` — not re-tested this session

## Proof (jadzia VPS)

```text
# Direct API (localhost smoke)
{"lead_id":"1","sync_status":"success"}
1|deploy02-int004-20260626173245@flexgrafik.nl|game|420|bronze

# zzpackage PHP sync
2|deploy02-php-20260626173252@flexgrafik.nl|777|game10
```

## Architecture

```text
app saveLead → zzpackage /wp-json/fg/v1/leads → MySQL + fg_jadzia_sync_lead → jadzia POST /api/v1/leads
```

## App repo (uncommitted)

- ~~`fg-game-api.php` — INT-004 forward~~ → **committed** `c7091cb` on `feat/int-004-lead-sync-coi`
- PR: https://github.com/wozniaknorbert95-del/app.flexgrafik.nl/pull/119
- Handoff: `app.flexgrafik.nl/docs/handoffs/2026-06-26-deploy-int-004-leads.md`

## Rollback

Remove `FG_JADZIA_LEADS_*` from zzpackage wp-config; game still saves to MySQL.
