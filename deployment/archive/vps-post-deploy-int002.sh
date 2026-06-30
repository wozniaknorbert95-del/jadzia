#!/bin/bash
# Post-deploy INT-002: ensure secrets and schema on VPS. Run as root on jadzia VPS.
set -euo pipefail
JADZIA_DIR="${JADZIA_DIR:-/root/jadzia}"
ENV_FILE="${JADZIA_DIR}/.env"
SECRETS_FILE="${JADZIA_DIR}/data/.int002-secrets.env"

mkdir -p "${JADZIA_DIR}/data"

if ! grep -q '^WC_WEBHOOK_SECRET=' "$ENV_FILE" 2>/dev/null; then
  WC_SECRET=$(openssl rand -hex 32)
  echo "WC_WEBHOOK_SECRET=${WC_SECRET}" >> "$ENV_FILE"
  echo "WC_WEBHOOK_SECRET=${WC_SECRET}" > "$SECRETS_FILE"
  chmod 600 "$SECRETS_FILE"
  echo "WC_WEBHOOK_SECRET added"
else
  grep '^WC_WEBHOOK_SECRET=' "$ENV_FILE" > "$SECRETS_FILE"
  chmod 600 "$SECRETS_FILE"
  echo "WC_WEBHOOK_SECRET already set"
fi

if ! grep -q '^LEADS_API_KEY=' "$ENV_FILE" 2>/dev/null; then
  LEADS_KEY=$(openssl rand -hex 24)
  echo "LEADS_API_KEY=${LEADS_KEY}" >> "$ENV_FILE"
  echo "LEADS_API_KEY=${LEADS_KEY}" >> "$SECRETS_FILE"
  echo "LEADS_API_KEY added"
else
  echo "LEADS_API_KEY already set"
fi

cd "$JADZIA_DIR"
source venv/bin/activate
python3 -c "from agent.db import get_connection; get_connection(); print('schema_ok')"

systemctl restart jadzia
sleep 2
curl -sf http://localhost:8000/worker/health | head -c 120
echo ""
test -f "${JADZIA_DIR}/api/routes/webhooks.py" && echo "webhooks_route=ok"
sqlite3 "${JADZIA_DIR}/data/jadzia.db" "SELECT name FROM sqlite_master WHERE name IN ('orders','leads');"
