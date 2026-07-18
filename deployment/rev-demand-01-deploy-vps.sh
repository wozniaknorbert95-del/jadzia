#!/bin/bash
# REV-DEMAND-01 — deploy master to VPS (Dowódca-authorized)
set -euo pipefail

PROJECT_DIR="/opt/jadzia"
RUN_USER="jadzia"
BRANCH="master"
TARGET_SHA="${1:-}"
TS="$(date +%Y%m%d-%H%M%S)"
BACKUP="${PROJECT_DIR}/data/jadzia-pre-rev-demand-01-${TS}.db"

echo "=== 1) SQLite backup ==="
sudo -u "${RUN_USER}" sqlite3 "${PROJECT_DIR}/data/jadzia.db" ".backup '${BACKUP}'"
sudo -u "${RUN_USER}" sqlite3 "${BACKUP}" "PRAGMA integrity_check;"
echo "backup=${BACKUP}"

echo "=== 2) Deploy ${BRANCH} ==="
cd "${PROJECT_DIR}"
git fetch origin "${BRANCH}"
git checkout "${BRANCH}"
git pull --ff-only origin "${BRANCH}"
HEAD="$(git rev-parse HEAD)"
SHORT="$(git rev-parse --short HEAD)"
echo "head=${SHORT} full=${HEAD}"
if [[ -n "${TARGET_SHA}" ]]; then
  if [[ "${HEAD}" != "${TARGET_SHA}"* && "${HEAD}" != "${TARGET_SHA}" ]]; then
    echo "WARN: expected ${TARGET_SHA}, got ${HEAD}"
  fi
fi

echo "=== 3) Dependencies ==="
sudo -u "${RUN_USER}" bash -lc "cd ${PROJECT_DIR} && source venv/bin/activate && pip install -r requirements.txt -q"

echo "=== 4) Restart ==="
systemctl restart jadzia
sleep 4
systemctl is-active jadzia
curl -sf http://127.0.0.1:8000/worker/health | python3 -m json.tool | head -30

echo "=== 5) Schema disposition column ==="
sudo -u "${RUN_USER}" sqlite3 "${PROJECT_DIR}/data/jadzia.db" "PRAGMA table_info(leads);" | grep -E disposition || true

echo "=== 6) Widget CTA smoke (no pay) ==="
curl -sf -X POST http://127.0.0.1:8000/api/v1/widget/chat \
  -H 'Content-Type: application/json' \
  -d '{"session_id":"dogfood-deploy-demand","message":"Ik wil een offerte voor mijn bestelwagen"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('reply_ok', bool(d.get('reply'))); print('has_deeplink', bool(d.get('wizard_deeplink'))); print('cta_sku', d.get('cta_sku')); print('keys', sorted(d.keys()))"

echo "=== REV-DEMAND-01 deploy OK @ ${SHORT} ==="
