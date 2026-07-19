#!/bin/bash
# MKT-BRAIN-PRO F0 — deploy Data Truth Layer to VPS (in-session GO)
set -euo pipefail

PROJECT_DIR="/opt/jadzia"
RUN_USER="jadzia"
BRANCH="master"
TARGET_SHA="${1:-f28a938}"
TS="$(date +%Y%m%d-%H%M%S)"
BACKUP="${PROJECT_DIR}/data/jadzia-pre-mkt-brain-f0-${TS}.db"

echo "=== PRE ==="
cd "${PROJECT_DIR}"
echo "prev_tip=$(git rev-parse --short HEAD)"
systemctl is-active jadzia

echo "=== 1) SQLite backup ==="
sudo -u "${RUN_USER}" sqlite3 "${PROJECT_DIR}/data/jadzia.db" ".backup '${BACKUP}'"
sudo -u "${RUN_USER}" sqlite3 "${BACKUP}" "PRAGMA integrity_check;"
echo "backup=${BACKUP}"

echo "=== 2) Deploy ${BRANCH} ==="
git fetch origin "${BRANCH}"
git checkout "${BRANCH}"
git pull --ff-only origin "${BRANCH}"
HEAD="$(git rev-parse HEAD)"
SHORT="$(git rev-parse --short HEAD)"
echo "head=${SHORT} full=${HEAD}"
if [[ -n "${TARGET_SHA}" ]]; then
  if [[ "${HEAD}" != "${TARGET_SHA}"* && "${SHORT}" != "${TARGET_SHA}"* ]]; then
    echo "ABORT: expected ${TARGET_SHA}, got ${SHORT}"
    exit 1
  fi
  echo "tip_match=OK"
fi

echo "=== 3) Dependencies ==="
sudo -u "${RUN_USER}" bash -lc "cd ${PROJECT_DIR} && source venv/bin/activate && pip install -r requirements.txt -q"

echo "=== 4) DTL ingest interval (idempotent) ==="
ENV_FILE="${PROJECT_DIR}/.env"
if ! grep -q '^MARKETING_DTL_INGEST_INTERVAL_SECONDS=' "${ENV_FILE}" 2>/dev/null; then
  echo 'MARKETING_DTL_INGEST_INTERVAL_SECONDS=3600' >> "${ENV_FILE}"
  echo "env_added=MARKETING_DTL_INGEST_INTERVAL_SECONDS=3600"
else
  echo "env_dtl_interval_already_set"
fi

echo "=== 5) Restart ==="
systemctl restart jadzia
sleep 5
systemctl is-active jadzia
curl -sf http://127.0.0.1:8000/health
echo
curl -sf http://127.0.0.1:8000/worker/health | python3 -m json.tool | head -40

echo "=== 6) Schema DTL tables ==="
sudo -u "${RUN_USER}" sqlite3 "${PROJECT_DIR}/data/jadzia.db" \
  "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('marketing_raw_ingest','marketing_facts','data_quality_flags','order_margin_facts') ORDER BY name;"

echo "=== MKT-BRAIN-PRO F0 deploy OK @ ${SHORT} ==="
