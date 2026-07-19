# DEPLOY-03 proof — INT-009 analytics E2E (CLOSED)

**Date:** 2026-06-26  
**Gate:** DEPLOY-03  
**Status:** **PASS** (full — zzpackage property `528785553` verified 2026-06-27)

## Checklist

- [x] `GOOGLE_APPLICATION_CREDENTIALS` on jadzia VPS (`/root/jadzia/secrets/ga4-service-account.json`)
- [x] `GA4_PROPERTY_ID_APP=528764186` (FlexGrafik App, `G-0XN9Z7HS90`)
- [x] `GA4_PROPERTY_ID_ZZPACKAGE=528785553` (ZZPackage Shop, `G-L23DGTEKCD`) — **in .env**
- [x] SA Viewer on app property (528764186)
- [x] SA Viewer on zzpackage property (528785553) — **granted by Dowódca 2026-06-26; verified 2026-06-27**
- [x] `google-analytics-data` in jadzia venv (0.23.0)
- [x] Snapshot pipeline proof → `sync_status: success` (both sources)

## Proof

### Pipeline success (interim property read)

With `GA4_PROPERTY_ID_ZZPACKAGE=528764186` (same SA access as app) to validate COI pipeline:

```json
{
  "sync_status": "success",
  "period": "last_7_days",
  "sources": {
    "app": {"active_users": 9, "sessions": 13, "game_starts": 5},
    "zzpackage": {"sessions": 13, "conversions": 0, "purchase_revenue": 0.0, "aov": 0.0}
  },
  "errors": []
}
```

### Production .env (restored)

```
GA4_PROPERTY_ID_APP=528764186
GA4_PROPERTY_ID_ZZPACKAGE=528785553
```

### Live snapshot (528785553) — 2026-06-27

After `systemctl restart jadzia` + SA Viewer grant:

```json
{
  "sync_status": "success",
  "period": "last_7_days",
  "sources": {
    "app": {"active_users": 9, "sessions": 12, "game_starts": 3},
    "zzpackage": {"sessions": 23, "conversions": 0, "purchase_revenue": 0.0, "aov": 0.0}
  },
  "errors": []
}
```

Script: `deployment/verify-ga4-zzpackage.sh` → **PASS**

### Grant SA on zzpackage property (one-time)

URL: https://analytics.google.com/analytics/web/#/a337818458p528785553/admin/property/access-management

Add **Viewer**: `quietforge-ga-reader-712@flexgrafik.iam.gserviceaccount.com`

Scripts attempted: `services/scripts/ga4-add-zzpackage-viewer*.mjs` (Chrome session not available for full UI automation).

## Secrets location (nie w repo)

- VPS: `/root/jadzia/.env` + `/root/jadzia/secrets/ga4-service-account.json`
- Local source: `C:/Users/FlexGrafik/.config/quietforge-ga-sa.json` (not in repo)

## Zamknięcie gate

INT-009 pipeline **LIVE** on VPS. Both `app` and `zzpackage` sources return metrics (`sync_status: success`, `errors: []`).
