# Handoff: Deploy closure COMPLETE (2026-07-05)

**Gate:** Zasada 11 manual deploy — **CLOSED**  
**VPS:** 185.243.54.115 `/opt/jadzia` @ `463e5e0`

## All requirements PASS

| Requirement | Result |
|-------------|--------|
| Deploy | git pull + venv + systemd restart |
| `JADZIA_ENV=production` | set in `.env` |
| `POST /chat` bez JWT | **401** |
| `prod-smoke.sh` | **8/8 PASS** (exit 0) |
| `WEEKLY_BRIEF_INTERVAL_SECONDS` | **604800** |

## Fix applied during closure

- **GA4 credentials path** — `.env` pointed to stale `/root/jadzia/secrets/...`; corrected to `/opt/jadzia/secrets/ga4-service-account.json` → analytics/snapshot smoke PASS

## Scripts added for repeatability

- `deployment/vps-deploy-closure.sh` — full closure runbook
- `deployment/vps-fix-ga4-path.sh` — GA4 path hotfix
- `docs/ops/PLAN-DEPLOY-CLOSURE-2026-07-05.md` — comprehensive checklist

## Still open (not this deploy)

- **S1-01** secret rotation + BFG — Dowódca only

## Next session

Edge hardening OR S1-01 OR B3.1 FB sense — per `todo.json`
