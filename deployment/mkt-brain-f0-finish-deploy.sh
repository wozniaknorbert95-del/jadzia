#!/bin/bash
# Finish F0 deploy after dirty-tree abort (backup already done)
set -euo pipefail

cd /opt/jadzia
echo "=== dirty cleanup ==="
rm -rf agent/marketing
rm -f tests/unit/test_dtl_f0.py
git fetch origin master
git reset --hard origin/master
SHORT="$(git rev-parse --short HEAD)"
echo "head=${SHORT}"
if [ "${SHORT}" != "f28a938" ]; then
  echo "ABORT tip=${SHORT}"
  exit 1
fi
echo "tip_match=OK"

echo "=== deps ==="
sudo -u jadzia bash -lc 'cd /opt/jadzia && source venv/bin/activate && pip install -r requirements.txt -q'

ENV_FILE=/opt/jadzia/.env
if ! grep -q '^MARKETING_DTL_INGEST_INTERVAL_SECONDS=' "${ENV_FILE}" 2>/dev/null; then
  echo 'MARKETING_DTL_INGEST_INTERVAL_SECONDS=3600' >> "${ENV_FILE}"
  echo "env_added=DTL_INTERVAL"
else
  echo "env_dtl_interval_already_set"
fi

echo "=== restart ==="
systemctl restart jadzia
sleep 5
systemctl is-active jadzia
curl -sf http://127.0.0.1:8000/health
echo

echo "=== schema ==="
sudo -u jadzia sqlite3 /opt/jadzia/data/jadzia.db \
  "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('marketing_raw_ingest','marketing_facts','data_quality_flags','order_margin_facts') ORDER BY name;"

echo "=== DEPLOY_OK @ ${SHORT} ==="
