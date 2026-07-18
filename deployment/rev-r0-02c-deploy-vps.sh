#!/bin/bash
# REV-R0-02C — non-interactive Jadzia consumer deploy on VPS
set -euo pipefail

BRANCH="feat/rev-r0-02c-int002-consumer"
PROJECT_DIR="/opt/jadzia"
RUN_USER="jadzia"
TS="$(date +%Y%m%d-%H%M%S)"
BACKUP="${PROJECT_DIR}/data/jadzia-pre-int002-v2-${TS}.db"

echo "=== 1) SQLite backup ==="
sudo -u "${RUN_USER}" sqlite3 "${PROJECT_DIR}/data/jadzia.db" ".backup '${BACKUP}'"
sudo -u "${RUN_USER}" sqlite3 "${BACKUP}" "PRAGMA integrity_check;"
echo "backup=${BACKUP}"

echo "=== 2) Deploy consumer branch ==="
cd "${PROJECT_DIR}"
git fetch origin "${BRANCH}"
git checkout "${BRANCH}"
git pull --ff-only origin "${BRANCH}"
echo "head=$(git rev-parse --short HEAD)"

echo "=== 3) Dependencies ==="
sudo -u "${RUN_USER}" bash -lc "cd ${PROJECT_DIR} && source venv/bin/activate && pip install -r requirements.txt -q"

echo "=== 4) Restart service ==="
systemctl restart jadzia
sleep 3
systemctl is-active jadzia
curl -sf http://127.0.0.1:8000/worker/health | python3 -m json.tool | head -20

echo "=== 5) Schema verify ==="
sudo -u "${RUN_USER}" sqlite3 "${PROJECT_DIR}/data/jadzia.db" "PRAGMA table_info(orders);" | grep -E 'schema_version|payment_status|classification|checkout_id|attribution_json' || true
sudo -u "${RUN_USER}" sqlite3 "${PROJECT_DIR}/data/jadzia.db" "PRAGMA index_list(orders);" | grep checkout || true

echo "=== 6) Prod smoke ==="
bash "${PROJECT_DIR}/deployment/prod-smoke.sh"

echo "=== REV-R0-02C consumer deploy OK ==="
