# Deploy checklist: S2-01 Auth Hardening (Dowódca)

**Gate:** Manual deploy only (Zasada 11)

## Pre-deploy

- [ ] Firewall allowlist on `:8000` (known IPs only)
- [ ] Backup: `cp /opt/jadzia/data/jadzia.db data/jadzia.db.bak.$(date +%Y%m%d-%H%M%S)`

## VPS `.env` (add/confirm)

```env
JADZIA_ENV=production
# or REQUIRE_SECRETS=1
JWT_SECRET=<set>
WC_WEBHOOK_SECRET=<match zzpackage FG_JADZIA_WEBHOOK_SECRET>
LEADS_API_KEY=<match app.flexgrafik.nl>
```

## Deploy

1. Upload code via `deployment/deploy-to-vps.sh`
2. `systemctl restart jadzia`
3. `bash deployment/prod-smoke.sh`

## Post-deploy proof

```bash
# Must return 401 without token
curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"test","chat_id":"proof"}'
# Expected: 401

# With JWT — 200 or 500 (not 401)
TOKEN=$(JWT_SECRET="$JWT_SECRET" python3 -c 'import os,jwt; print(jwt.encode({"sub":"smoke"}, os.environ["JWT_SECRET"], algorithm="HS256"))')
curl -s -H "Authorization: Bearer $TOKEN" -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"test","chat_id":"proof"}'
```

## Rollback

Restore previous code + restart service. JWT removal from `.env` temporarily re-opens routes (not recommended).
