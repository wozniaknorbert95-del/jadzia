#!/bin/bash
set -euo pipefail
cd /opt/jadzia
echo "=== telegram env present? ==="
grep -E '^(TELEGRAM_BOT_TOKEN|TELEGRAM_ADMIN_CHAT_ID)=' .env | sed 's/=.*/=***/' || true
TOKEN="$(sudo -u jadzia bash -lc 'cd /opt/jadzia && ./venv/bin/python3 scripts/jwt_token.py' | tail -n1 | tr -d '\r')"
# Force a cycle with mocked? just re-run and inspect logs
journalctl -u jadzia -n 40 --no-pager | grep -i 'mb\.\|marketing brain\|mb.telegram\|mb.runtime' | tail -20 || true
curl -sf -X POST http://127.0.0.1:8000/api/v1/commander/marketing/brain/cycle \
  -H "Authorization: Bearer ${TOKEN}" -H 'Content-Type: application/json' -d '{}' \
  -o /tmp/mb-cycle3.json
python3 - <<'PY'
import json
print(json.load(open("/tmp/mb-cycle3.json")))
PY
