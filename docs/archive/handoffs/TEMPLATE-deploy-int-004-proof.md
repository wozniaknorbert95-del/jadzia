# TEMPLATE — DEPLOY-02 INT-004 lead E2E proof

**Gate:** DEPLOY-02 (after DEPLOY-01 + P1-01 code deployed)

## Checklist

- [ ] `LEADS_API_KEY` set on jadzia VPS `.env`
- [ ] app.flexgrafik.nl configured with same key + jadzia URL
- [ ] Test lead POST → row in `leads` table
- [ ] Duplicate email → `sync_status: duplicate`

## Smoke curl

```bash
curl -sS -X POST "http://185.243.54.115:8000/api/v1/leads" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <LEADS_API_KEY>" \
  -d '{"email":"test@example.nl","name":"Test","source":"game","consent_status":true,"game_score":100,"reward_tier":"bronze"}'
```

Expected: `{"lead_id":"1","sync_status":"success"}`
