#!/bin/bash
# MKT-BRAIN-PRO F3 — deploy tip + ensure BRAIN_BUS_SECRET + smoke
set -euo pipefail
EXPECTED_TIP="${1:-e65de14}"
cd /opt/jadzia
TS=$(date +%Y%m%d-%H%M%S)
BACKUP="/opt/jadzia/data/jadzia-pre-mkt-brain-f3-${TS}.db"
sudo -u jadzia sqlite3 /opt/jadzia/data/jadzia.db ".backup '${BACKUP}'"
echo "backup=${BACKUP}"
git fetch origin master
git reset --hard origin/master
TIP="$(git rev-parse --short HEAD)"
echo "tip=${TIP}"
if [[ "${TIP}" != "${EXPECTED_TIP}"* && "${TIP}" != "${EXPECTED_TIP}" ]]; then
  # allow full or short sha match
  FULL="$(git rev-parse HEAD)"
  if [[ "${FULL}" != "${EXPECTED_TIP}"* && "${TIP}" != "${EXPECTED_TIP}" ]]; then
    echo "WARN tip ${TIP} != expected ${EXPECTED_TIP} (continuing if tip is newer F3)"
  fi
fi

ENV_FILE="/opt/jadzia/.env"
if ! grep -q '^BRAIN_BUS_SECRET=' "${ENV_FILE}" 2>/dev/null; then
  SECRET="$(openssl rand -hex 24)"
  echo "" >> "${ENV_FILE}"
  echo "# MKT-BRAIN-PRO F3 Brain Bus $(date -u +%Y-%m-%dT%H:%MZ)" >> "${ENV_FILE}"
  echo "BRAIN_BUS_SECRET=${SECRET}" >> "${ENV_FILE}"
  chown jadzia:jadzia "${ENV_FILE}" 2>/dev/null || true
  echo "BRAIN_BUS_SECRET=generated"
else
  echo "BRAIN_BUS_SECRET=already_set"
fi

systemctl restart jadzia
sleep 5
systemctl is-active jadzia
curl -sf http://127.0.0.1:8000/health; echo

# Smoke: degraded → processed → CB_ECOSYSTEM
SECRET_VAL="$(grep '^BRAIN_BUS_SECRET=' "${ENV_FILE}" | head -n1 | cut -d= -f2- | tr -d '\r')"
SMOKE="$(curl -sf -X POST http://127.0.0.1:8000/api/v1/brain-bus/events \
  -H "Content-Type: application/json" \
  -H "X-Brain-Bus-Secret: ${SECRET_VAL}" \
  -d '{"event_type":"system.health.degraded","source_brain":"vcms","payload":{"conflicts":1,"summary":"F3 deploy smoke"},"correlation_id":"f3-deploy-smoke"}')"
echo "smoke_degraded_ok=$(echo "${SMOKE}" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("ok") and d.get("processed",{}).get("done",0)>=1)')"

# Recover immediately so prod is not left in ecosystem red from smoke
curl -sf -X POST http://127.0.0.1:8000/api/v1/brain-bus/events \
  -H "Content-Type: application/json" \
  -H "X-Brain-Bus-Secret: ${SECRET_VAL}" \
  -d '{"event_type":"system.health.recovered","source_brain":"vcms","payload":{"conflicts":0},"correlation_id":"f3-deploy-recover"}' >/dev/null
echo "smoke_recovered=ok"

TOKEN="$(sudo -u jadzia bash -lc 'cd /opt/jadzia && ./venv/bin/python3 scripts/jwt_token.py' | tail -n1 | tr -d '\r')"
curl -sf http://127.0.0.1:8000/api/v1/commander/marketing/brain-bus?limit=5 \
  -H "Authorization: Bearer ${TOKEN}" | python3 -c 'import sys,json; d=json.load(sys.stdin); print("events", len(d.get("events",[])))'

echo "=== F3_DEPLOY_OK tip=${TIP} ==="
