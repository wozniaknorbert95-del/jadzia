# DEPLOY-02 — INT-004 lead E2E proof (CLOSED)

**Date:** 2026-06-26  
**Gate:** DEPLOY-02  
**Status:** **PASS — gate closed**

## Checklist

- [x] `LEADS_API_KEY` set on jadzia VPS `.env`
- [x] zzpackage `wp-config.php`: `FG_JADZIA_LEADS_URL` + `FG_JADZIA_LEADS_API_KEY`
- [x] `fg-game-api.php` v1.3 on zzpackage mu-plugins (`fg_jadzia_sync_lead`)
- [x] app.flexgrafik.nl merged + deployed (`917b630`, GHA run `28249495347`)
- [x] zzpackage API E2E: `POST /wp-json/fg/v1/leads` → row in `leads`
- [x] Duplicate email → `sync_status: duplicate`
- [x] Prod bundle `index-CYmIa0Tf.js` live (HTTP smoke pass)

## Proof

### Deploy

| Item | Value |
|------|-------|
| app commit | `917b630` (merge PR #119) |
| GHA deploy | https://github.com/wozniaknorbert95-del/app.flexgrafik.nl/actions/runs/28249495347 |
| HTTP smoke | app-root 200, hashed-js 200, player-webp 200 |

### E2E lead (zzpackage → jadzia)

```text
POST /wp-json/fg/v1/leads → HTTP 201 {"status":"ok"}
EMAIL=int004-e2e-20260626175956@flexgrafik.nl
jadzia leads row: 3|int004-e2e-20260626175956@flexgrafik.nl|game|250|stickers
```

### Duplicate

```text
POST /api/v1/leads (same email) → {"lead_id":"3","sync_status":"duplicate"}
```

## Architecture

```text
app saveLead → zzpackage /wp-json/fg/v1/leads → MySQL + fg_jadzia_sync_lead → jadzia POST /api/v1/leads
```

## Rollback

Remove `FG_JADZIA_LEADS_*` from zzpackage wp-config; redeploy previous app commit.
