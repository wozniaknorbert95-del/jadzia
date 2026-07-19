#!/bin/bash
# MKT-BRAIN-PRO F1 deploy
set -euo pipefail

PROJECT_DIR=/opt/jadzia
RUN_USER=jadzia
TARGET_SHA="${1:-aff91ff}"
TS="$(date +%Y%m%d-%H%M%S)"
BACKUP="${PROJECT_DIR}/data/jadzia-pre-mkt-brain-f1-${TS}.db"

cd "${PROJECT_DIR}"
echo "prev=$(git rev-parse --short HEAD)"

echo "=== backup ==="
sudo -u "${RUN_USER}" sqlite3 "${PROJECT_DIR}/data/jadzia.db" ".backup '${BACKUP}'"
sudo -u "${RUN_USER}" sqlite3 "${BACKUP}" "PRAGMA integrity_check;"
echo "backup=${BACKUP}"

echo "=== pull ==="
git fetch origin master
git reset --hard "origin/master"
SHORT="$(git rev-parse --short HEAD)"
echo "head=${SHORT}"
case "${SHORT}" in
  ${TARGET_SHA}*) echo tip_ok ;;
  *) echo "WARN tip=${SHORT} expected~${TARGET_SHA}" ;;
esac

ENV_FILE="${PROJECT_DIR}/.env"
upsert() {
  local k="$1" v="$2"
  if grep -q "^${k}=" "${ENV_FILE}" 2>/dev/null; then
    sed -i "s|^${k}=.*|${k}=${v}|" "${ENV_FILE}"
  else
    echo "${k}=${v}" >> "${ENV_FILE}"
  fi
  echo "env ${k}=set"
}
upsert MB_MODE shadow
upsert MARKETING_BRAIN_INTERVAL_SECONDS 3600
# keep DTL interval
if ! grep -q '^MARKETING_DTL_INGEST_INTERVAL_SECONDS=' "${ENV_FILE}"; then
  upsert MARKETING_DTL_INGEST_INTERVAL_SECONDS 3600
fi

sudo -u "${RUN_USER}" bash -lc "cd ${PROJECT_DIR} && source venv/bin/activate && pip install -r requirements.txt -q"
systemctl restart jadzia
sleep 5
systemctl is-active jadzia
curl -sf http://127.0.0.1:8000/health
echo

sudo -u "${RUN_USER}" sqlite3 "${PROJECT_DIR}/data/jadzia.db" \
  "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('marketing_shadow_log','marketing_hypotheses','brain_events') ORDER BY name;"

TOKEN="$(sudo -u jadzia bash -lc 'cd /opt/jadzia && ./venv/bin/python3 scripts/jwt_token.py' | tail -n1 | tr -d '\r')"
curl -sf -X POST http://127.0.0.1:8000/api/v1/commander/marketing/brain/cycle \
  -H "Authorization: Bearer ${TOKEN}" \
  -H 'Content-Type: application/json' \
  -d '{}' \
  -o /tmp/mb-cycle.json
python3 - <<'PY'
import json
d=json.load(open("/tmp/mb-cycle.json"))
print("cycle_ok", d.get("ok"), "records", d.get("records"), "tg", d.get("telegram_sent"), "events", d.get("brain_events"))
PY

curl -sf http://127.0.0.1:8000/api/v1/commander/marketing/shadow?limit=5 \
  -H "Authorization: Bearer ${TOKEN}" \
  -o /tmp/mb-shadow.json
python3 - <<'PY'
import json
d=json.load(open("/tmp/mb-shadow.json"))
print("shadow_n", len(d.get("shadow") or []), "hyp_n", len(d.get("hypotheses") or []), "mode", d.get("mb_mode"))
if d.get("shadow"):
    s=d["shadow"][0]
    print("latest", s.get("action_id"), s.get("heuristic_rule_id"), s.get("proposed_action"), s.get("mb_mode"))
PY

echo "=== F1_DEPLOY_OK @ ${SHORT} ==="
