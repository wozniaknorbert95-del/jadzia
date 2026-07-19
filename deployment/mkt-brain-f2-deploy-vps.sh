#!/bin/bash
set -euo pipefail
cd /opt/jadzia
TS=$(date +%Y%m%d-%H%M%S)
BACKUP="/opt/jadzia/data/jadzia-pre-mkt-brain-f2-${TS}.db"
sudo -u jadzia sqlite3 /opt/jadzia/data/jadzia.db ".backup '${BACKUP}'"
echo "backup=${BACKUP}"
git fetch origin master
git reset --hard origin/master
echo "tip=$(git rev-parse --short HEAD)"
systemctl restart jadzia
sleep 5
systemctl is-active jadzia
curl -sf http://127.0.0.1:8000/health; echo
sudo -u jadzia sqlite3 /opt/jadzia/data/jadzia.db \
  "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('marketing_approval_tokens','circuit_breaker_events') ORDER BY name;"
TOKEN="$(sudo -u jadzia bash -lc 'cd /opt/jadzia && ./venv/bin/python3 scripts/jwt_token.py' | tail -n1 | tr -d '\r')"
curl -sf http://127.0.0.1:8000/api/v1/commander/marketing/breakers \
  -H "Authorization: Bearer ${TOKEN}" | python3 -m json.tool
echo "=== F2_DEPLOY_OK ==="
