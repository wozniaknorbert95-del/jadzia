#!/bin/bash
# Organic DTL + CEO brief bridge deploy smoke
set -euo pipefail
EXPECTED="${1:-}"
cd /opt/jadzia
TS=$(date +%Y%m%d-%H%M%S)
sudo -u jadzia sqlite3 /opt/jadzia/data/jadzia.db \
  ".backup '/opt/jadzia/data/jadzia-pre-org-ceo-${TS}.db'"
git fetch origin master
git reset --hard origin/master
TIP=$(git rev-parse --short HEAD)
echo "tip=${TIP}"
if [[ -n "${EXPECTED}" && "${TIP}" != "${EXPECTED}"* ]]; then
  echo "WARN tip mismatch expected=${EXPECTED}"
fi
grep -q '^BRIEF_CEO_PRIORITY_ENABLED=' .env 2>/dev/null || echo 'BRIEF_CEO_PRIORITY_ENABLED=1' >> .env
systemctl restart jadzia
sleep 5
systemctl is-active jadzia
curl -sf http://127.0.0.1:8000/health; echo
TOKEN=$(sudo -u jadzia bash -lc 'cd /opt/jadzia && ./venv/bin/python3 scripts/jwt_token.py' | tail -n1 | tr -d '\r')
curl -sf -X POST http://127.0.0.1:8000/api/v1/commander/marketing/dtl/ingest \
  -H "Authorization: Bearer ${TOKEN}" | python3 -c 'import sys,json;d=json.load(sys.stdin);print("dtl_ok",d.get("steps_ok"),"err",d.get("steps_error"));print([s.get("source")+":"+str(s.get("status")) for s in d.get("steps",[]) if s.get("source")=="facebook_organic"])'
curl -sf -X POST http://127.0.0.1:8000/api/v1/commander/marketing/brain/cycle \
  -H "Authorization: Bearer ${TOKEN}" | python3 -c 'import sys,json;d=json.load(sys.stdin);print("cycle",d.get("ok"),"mem",d.get("memory_sources"))'
echo "=== ORG_CEO_DEPLOY_OK tip=${TIP} ==="
