# Deploy proof: S2-01 remediation (2026-07-03)

**VPS:** 185.243.54.115 `/opt/jadzia`  
**Git:** `origin/master` @ `47149a7`  
**Status:** DEPLOYED + SERVICE ACTIVE

## Deploy steps executed

1. `git push origin master` — commits `00c94dd`, `47149a7`
2. VPS `git fetch && git reset --hard origin/master`
3. `JADZIA_ENV=production` appended to `.env` (secrets already present)
4. venv recreated (`python3 -m venv venv` + `pip install -r requirements.txt`)
5. `jadzia.service` updated → `uvicorn main:app` (no reload)
6. `systemctl reset-failed && systemctl restart jadzia`

## Verification

| Check | Result |
|-------|--------|
| `systemctl is-active jadzia` | **active** |
| Process | `/opt/jadzia/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000` |
| `prod-smoke.sh` | **7/8 PASS** (analytics/snapshot 1 fail — GA4/JWT smoke quirk, service up) |
| `POST /chat` bez JWT | **401** |
| `worker/health` | OK |
| WC_WEBHOOK_SECRET | configured |
| GA4 env | configured |
| FB publish env | configured |
| Orders in DB | 4 |

## Auth proof command

```bash
curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"proof","chat_id":"deploy-proof"}'
# → 401
```

## Ops notes

- Old venv had broken shebang (`#!/root/jadzia/venv/bin/python3`) — fixed by venv recreate
- `systemctl reset-failed` required after StartLimitBurst during failed restarts

## Remaining (Dowódca)

- **S1-01** secret rotation + BFG — see `2026-07-03-s1-01-secret-rotation-checklist.md`
- Optional: `docs/ops/VPS-EDGE-HARDENING.md` (firewall/nginx)
- Optional: `WEEKLY_BRIEF_INTERVAL_SECONDS=604800` in `.env`
