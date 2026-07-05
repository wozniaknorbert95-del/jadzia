#!/usr/bin/env bash
set -euo pipefail
ENV=/opt/jadzia/.env
CRED=/opt/jadzia/secrets/ga4-service-account.json
if grep -q '^GOOGLE_APPLICATION_CREDENTIALS=' "$ENV"; then
  sed -i "s|^GOOGLE_APPLICATION_CREDENTIALS=.*|GOOGLE_APPLICATION_CREDENTIALS=${CRED}|" "$ENV"
else
  echo "GOOGLE_APPLICATION_CREDENTIALS=${CRED}" >> "$ENV"
fi
chown jadzia:jadzia "$ENV" "$CRED"
chmod 640 "$ENV" "$CRED"
systemctl restart jadzia
sleep 8
echo "SERVICE: $(systemctl is-active jadzia)"
bash /opt/jadzia/deployment/prod-smoke.sh
echo "SMOKE_EXIT: $?"
