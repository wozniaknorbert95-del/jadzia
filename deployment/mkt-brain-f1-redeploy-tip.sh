#!/bin/bash
set -euo pipefail
cd /opt/jadzia
git fetch origin master
git reset --hard origin/master
echo "tip=$(git rev-parse --short HEAD)"
echo "=== allowlist/admin present? ==="
grep -E '^(ALLOWED_TELEGRAM_USERS|TELEGRAM_ADMIN_CHAT_ID)=' .env | sed 's/=.*/=***/' || echo "NONE"
systemctl restart jadzia
sleep 5
systemctl is-active jadzia
curl -sf http://127.0.0.1:8000/health
echo
TOKEN="$(sudo -u jadzia bash -lc 'cd /opt/jadzia && ./venv/bin/python3 scripts/jwt_token.py' | tail -n1 | tr -d '\r')"
curl -sf -X POST http://127.0.0.1:8000/api/v1/commander/marketing/brain/cycle \
  -H "Authorization: Bearer ${TOKEN}" \
  -H 'Content-Type: application/json' \
  -d '{}' | python3 -m json.tool
journalctl -u jadzia -n 30 --no-pager | grep -i 'mb.telegram\|mb.runtime' | tail -10 || true
echo "=== DONE ==="
