#!/bin/bash
# MKT-BRAIN-PRO Program Close — deploy tip + fb-health + weekly-draft evidence
set -euo pipefail

EXPECTED="${1:-}"
PROJECT_DIR="/opt/jadzia"
RUN_USER="jadzia"
TS="$(date +%Y%m%d-%H%M%S)"
BACKUP="${PROJECT_DIR}/data/jadzia-pre-program-close-${TS}.db"

echo "=== PRE ==="
cd "${PROJECT_DIR}"
echo "prev_tip=$(git rev-parse --short HEAD)"
systemctl is-active jadzia

echo "=== 1) SQLite backup ==="
sudo -u "${RUN_USER}" sqlite3 "${PROJECT_DIR}/data/jadzia.db" ".backup '${BACKUP}'"
sudo -u "${RUN_USER}" sqlite3 "${BACKUP}" "PRAGMA integrity_check;"
echo "backup=${BACKUP}"

echo "=== 2) Pull master ==="
git fetch origin master
git reset --hard origin/master
TIP="$(git rev-parse --short HEAD)"
echo "tip=${TIP}"
if [[ -n "${EXPECTED}" && "${TIP}" != "${EXPECTED}"* ]]; then
  echo "ABORT tip mismatch expected=${EXPECTED} got=${TIP}"
  exit 1
fi

ENV_FILE="${PROJECT_DIR}/.env"
if ! grep -q '^MARKETING_WEEKLY_SCORECARD_INTERVAL_SECONDS=' "${ENV_FILE}" 2>/dev/null; then
  echo 'MARKETING_WEEKLY_SCORECARD_INTERVAL_SECONDS=604800' >> "${ENV_FILE}"
  echo "env_added=WEEKLY_SCORECARD_INTERVAL"
fi

echo "=== 3) Restart ==="
systemctl restart jadzia
sleep 5
systemctl is-active jadzia
curl -sf http://127.0.0.1:8000/health; echo

TOKEN="$(sudo -u "${RUN_USER}" bash -lc 'cd /opt/jadzia && ./venv/bin/python3 scripts/jwt_token.py' | tail -n1 | tr -d '\r')"

echo "=== 4) fb-health ==="
curl -sf "http://127.0.0.1:8000/api/v1/commander/marketing/fb-health" \
  -H "Authorization: Bearer ${TOKEN}" \
  | python3 -c 'import sys,json;d=json.load(sys.stdin);print("fb_ok",d.get("ok"),"has_read_insights",d.get("has_read_insights"),"scopes",d.get("scopes"),"msg",(d.get("message_pl") or "")[:80])'

echo "=== 5) weekly-draft ==="
curl -sf "http://127.0.0.1:8000/api/v1/commander/marketing/weekly-draft" \
  -H "Authorization: Bearer ${TOKEN}" \
  | python3 -c 'import sys,json;d=json.load(sys.stdin);k=d.get("kpis") or {};print("week",d.get("iso_week"),"leads",k.get("leads"),"spend",k.get("spend_eur"),"cpl",k.get("cpl"),"decision",d.get("decision"))'

echo "=== PROGRAM_CLOSE_DEPLOY_OK tip=${TIP} ==="
