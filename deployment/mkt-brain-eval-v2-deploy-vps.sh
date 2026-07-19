#!/bin/bash
# MKT-BRAIN-PRO eval-pack v2 (+ weekly nudge) deploy smoke
set -euo pipefail
EXPECTED="${1:-}"
cd /opt/jadzia
TS=$(date +%Y%m%d-%H%M%S)
sudo -u jadzia sqlite3 /opt/jadzia/data/jadzia.db \
  ".backup '/opt/jadzia/data/jadzia-pre-eval-v2-${TS}.db'"
git fetch origin master
git reset --hard origin/master
TIP=$(git rev-parse --short HEAD)
echo "tip=${TIP}"
if [[ -n "${EXPECTED}" && "${TIP}" != "${EXPECTED}"* ]]; then
  echo "WARN tip mismatch expected=${EXPECTED}"
fi
grep -q '^MARKETING_EVAL_PUSH_INTERVAL_SECONDS=' .env 2>/dev/null \
  || echo 'MARKETING_EVAL_PUSH_INTERVAL_SECONDS=604800' >> .env
systemctl restart jadzia
sleep 5
systemctl is-active jadzia
curl -sf http://127.0.0.1:8000/health; echo
TOKEN=$(sudo -u jadzia bash -lc 'cd /opt/jadzia && ./venv/bin/python3 scripts/jwt_token.py' | tail -n1 | tr -d '\r')
curl -sf "http://127.0.0.1:8000/api/v1/commander/marketing/shadow/accuracy?window_days=14" \
  -H "Authorization: Bearer ${TOKEN}" \
  | python3 -c 'import sys,json;d=json.load(sys.stdin);print("accuracy",d.get("accuracy"),"n",d.get("n_scored"),"gate",d.get("gate_ready"),d.get("gate_reason"))'
curl -sf "http://127.0.0.1:8000/api/v1/commander/marketing/shadow/eval-pack?limit=5" \
  -H "Authorization: Bearer ${TOKEN}" \
  | python3 -c 'import sys,json;d=json.load(sys.stdin);print("pack",d.get("pack_version"),"n",d.get("n"))'
# Manual push smoke (1 card max via API limit) — proves Telegram path without flooding
curl -sf -X POST "http://127.0.0.1:8000/api/v1/commander/marketing/shadow/eval-push?limit=1&window_days=14" \
  -H "Authorization: Bearer ${TOKEN}" \
  | python3 -c 'import sys,json;d=json.load(sys.stdin);print("eval_push",d.get("ok"),"sent",d.get("sent"),d.get("message","")[:80])'
sudo -u jadzia sqlite3 /opt/jadzia/data/jadzia.db \
  "SELECT name FROM sqlite_master WHERE name='marketing_shadow_eval';"
echo "=== EVAL_V2_DEPLOY_OK tip=${TIP} ==="
