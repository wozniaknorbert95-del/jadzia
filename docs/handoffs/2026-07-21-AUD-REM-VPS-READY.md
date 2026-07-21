# READY_FOR_HUMAN — VPS deploy + verify (Wave1–4)

**Date:** 2026-07-21  
**Tasks:** FAZA 0 deploy smoke + `AUD-REM-VPS-VERIFY-01`  
**Authority:** requires **fresh Dowódca GO** (`standing_go_closeout=false`)  
**Hard STOP:** no autonomous SSH/deploy from agent

## Pre-merge tip

- GitHub `master`: `da46c49` (PR #9 Wave1–2) + Wave3–4 PR when merged

## Env checklist (VPS `/opt/jadzia/.env`)

| Variable | Required |
|----------|----------|
| `TELEGRAM_WEBHOOK_SECRET` | Yes — native header must match |
| `PUBLIC_API_DOCS_ENABLED` | `0` / unset |
| `WIDGET_CHAT_RATE_LIMIT` | optional (default 30) |
| `INGRESS_RATE_SALT` | random prod salt |
| `WEBHOOK_CALLBACK_ALLOWLIST` | HTTPS hosts |
| `SSH_KNOWN_HOSTS_PATH` / `SSH_HOST_KEY_FINGERPRINT` | HITL pin |
| `WP_HEALTH_CHECK_URL` or `SHOP_URL` | health target |

## Deploy sequence (Commander)

```bash
# 1. Backup
sudo -u jadzia sqlite3 /opt/jadzia/data/jadzia.db \
  ".backup '/opt/jadzia/data/jadzia-pre-deploy-$(date +%Y%m%d-%H%M%S).db'"

# 2. Pull (no local DB upload)
cd /opt/jadzia && git fetch origin master && git pull --ff-only origin master
git rev-parse --short HEAD

# 3. Deps
sudo -u jadzia bash -lc 'cd /opt/jadzia && source venv/bin/activate && \
  pip install --require-hashes -r requirements.lock -q'

# 4. Restart (single process)
sudo systemctl restart jadzia
sleep 5
systemctl is-active jadzia
```

## Smoke

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/docs          # expect 404
curl -sf http://127.0.0.1:8000/worker/health | head
# Widget: confirm session_id round-trip from flexgrafik-nl chat-widget.js
# Telegram: wrong X-Telegram-Bot-Api-Secret-Token → reject
```

## Verify checklist (AUD-REM-VPS-VERIFY-01)

1. HEAD `/opt/jadzia`, unit, process count (=1)
2. External HTTP codes (OpenAPI, status, health, admin sans JWT)
3. `PRAGMA integrity_check;` + `journal_mode` (expect wal) + backup list
4. Bind :8000, nginx, firewall
5. Non-mutating smoke only
6. Tip sync vs docs
7. No public Chroma server
8. Aneks → then update production UNVERIFIED → PASS/FAIL

## GO prompt

```text
GO VPS deploy+verify AUD-REM-VPS-VERIFY-01 tip <sha>
```
