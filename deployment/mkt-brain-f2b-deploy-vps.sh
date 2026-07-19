#!/bin/bash
# MKT-BRAIN-PRO F2b — campaign memory + eval-pack deploy
set -euo pipefail
EXPECTED_TIP="${1:-}"
cd /opt/jadzia
TS=$(date +%Y%m%d-%H%M%S)
BACKUP="/opt/jadzia/data/jadzia-pre-mkt-brain-f2b-${TS}.db"
sudo -u jadzia sqlite3 /opt/jadzia/data/jadzia.db ".backup '${BACKUP}'"
echo "backup=${BACKUP}"
git fetch origin master
git reset --hard origin/master
TIP="$(git rev-parse --short HEAD)"
echo "tip=${TIP}"
if [[ -n "${EXPECTED_TIP}" && "${TIP}" != "${EXPECTED_TIP}"* && "${TIP}" != "${EXPECTED_TIP}" ]]; then
  echo "WARN tip ${TIP} != expected ${EXPECTED_TIP}"
fi

if ! grep -q '^MB_CHROMA_PATH=' /opt/jadzia/.env 2>/dev/null; then
  echo "MB_CHROMA_PATH=/opt/jadzia/data/chroma/marketing" >> /opt/jadzia/.env
  echo "MB_CHROMA_PATH=set"
else
  echo "MB_CHROMA_PATH=already_set"
fi
mkdir -p /opt/jadzia/data/chroma/marketing
chown -R jadzia:jadzia /opt/jadzia/data/chroma 2>/dev/null || true

sudo -u jadzia bash -lc 'cd /opt/jadzia && source venv/bin/activate && pip install -r requirements.txt -q'
systemctl restart jadzia
sleep 6
systemctl is-active jadzia
curl -sf http://127.0.0.1:8000/health; echo

TOKEN="$(sudo -u jadzia bash -lc 'cd /opt/jadzia && ./venv/bin/python3 scripts/jwt_token.py' | tail -n1 | tr -d '\r')"
curl -sf http://127.0.0.1:8000/api/v1/commander/marketing/memory/status \
  -H "Authorization: Bearer ${TOKEN}" | python3 -m json.tool
curl -sf -X POST "http://127.0.0.1:8000/api/v1/commander/marketing/memory/sync?limit=50" \
  -H "Authorization: Bearer ${TOKEN}" | python3 -m json.tool
curl -sf "http://127.0.0.1:8000/api/v1/commander/marketing/shadow/eval-pack?limit=5" \
  -H "Authorization: Bearer ${TOKEN}" | python3 -c 'import sys,json; d=json.load(sys.stdin); print("eval_count", d.get("count"), "rubric", bool(d.get("rubric")))'
curl -sf -X POST http://127.0.0.1:8000/api/v1/commander/marketing/brain/cycle \
  -H "Authorization: Bearer ${TOKEN}" | python3 -c 'import sys,json; d=json.load(sys.stdin); print("cycle_ok", d.get("ok"), "memory", d.get("memory_sources") or d.get("memory_sync"))'
echo "=== F2B_DEPLOY_OK tip=${TIP} ==="
