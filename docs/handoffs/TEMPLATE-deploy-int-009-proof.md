# TEMPLATE — DEPLOY-03 INT-009 analytics E2E proof

**Gate:** DEPLOY-03 (after GA4 credentials + jadzia deploy with P1-02)

## Checklist

- [ ] `GOOGLE_APPLICATION_CREDENTIALS` on jadzia VPS
- [ ] `GA4_PROPERTY_ID_APP` + `GA4_PROPERTY_ID_ZZPACKAGE` set
- [ ] Service account Viewer on both GA4 properties
- [ ] `GET /api/v1/analytics/snapshot` → `sync_status: success`
- [ ] Both `sources.app` and `sources.zzpackage` populated

## Proof (bez PII)

| Field | Value |
|-------|-------|
| deploy_jadzia_commit | _fill_ |
| app_sessions_7d | _fill_ |
| zzpackage_conversions_7d | _fill_ |
| snapshot_response_sync_status | success |

## Smoke curl

```bash
TOKEN="<jwt>"
curl -sS -H "Authorization: Bearer $TOKEN" \
  "http://185.243.54.115:8000/api/v1/analytics/snapshot?period=7d"
```

## Secrets location (nie w repo)

- VPS: `/root/jadzia/.env` + `/root/jadzia/secrets/ga4-service-account.json`

## Zamknięcie gate

1. INT-009 → **LIVE** w `flexgrafik-meta/integration-contracts.md`
2. `todo.json`: DEPLOY-03 → `completed`
