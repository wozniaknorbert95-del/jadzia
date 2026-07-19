#!/bin/bash
# PLAN-14D: staff-eval + accuracy smoke
set -euo pipefail
EXPECTED="${1:-}"
cd /opt/jadzia
TS=$(date +%Y%m%d-%H%M%S)
sudo -u jadzia sqlite3 /opt/jadzia/data/jadzia.db \
  ".backup '/opt/jadzia/data/jadzia-pre-plan14d-${TS}.db'"
git fetch origin master
git reset --hard origin/master
TIP=$(git rev-parse --short HEAD)
echo "tip=${TIP}"
if [[ -n "${EXPECTED}" && "${TIP}" != "${EXPECTED}"* ]]; then
  echo "WARN tip mismatch expected=${EXPECTED}"
fi
systemctl restart jadzia
sleep 5
systemctl is-active jadzia
curl -sf http://127.0.0.1:8000/health; echo
TOKEN=$(sudo -u jadzia bash -lc 'cd /opt/jadzia && ./venv/bin/python3 scripts/jwt_token.py' | tail -n1 | tr -d '\r')
# Refresh shadow once so staff has something to score
curl -sf -X POST "http://127.0.0.1:8000/api/v1/commander/marketing/brain/cycle" \
  -H "Authorization: Bearer ${TOKEN}" \
  | python3 -c 'import sys,json;d=json.load(sys.stdin);print("cycle",d.get("ok"),"records",d.get("records"))'
curl -sf -X POST "http://127.0.0.1:8000/api/v1/commander/marketing/shadow/staff-eval?limit=20&window_days=14&notify=true" \
  -H "Authorization: Bearer ${TOKEN}" \
  | python3 -c 'import sys,json;d=json.load(sys.stdin);a=d.get("accuracy") or {};print("staff_scored",d.get("scored"),"tg",d.get("telegram_sent"),"acc",a.get("accuracy"),"n",a.get("n_scored"),"gate",a.get("gate_ready"))'
curl -sf "http://127.0.0.1:8000/api/v1/commander/marketing/shadow/accuracy?window_days=14" \
  -H "Authorization: Bearer ${TOKEN}" \
  | python3 -c 'import sys,json;d=json.load(sys.stdin);print("accuracy_final",d.get("accuracy"),"n",d.get("n_scored"),"gate",d.get("gate_ready"),d.get("gate_reason"))'
echo "=== PLAN14D_STAFF_EVAL_OK tip=${TIP} ==="
