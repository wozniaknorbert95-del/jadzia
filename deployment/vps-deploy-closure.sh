#!/usr/bin/env bash
# VPS deploy closure — run ON VPS as root
set -euo pipefail

JADZIA_ROOT="/opt/jadzia"
ENV_FILE="$JADZIA_ROOT/.env"

echo "=== Jadzia deploy closure ==="

cd "$JADZIA_ROOT"
git config --global --add safe.directory "$JADZIA_ROOT" 2>/dev/null || true

# Backup DB
if [ -f data/jadzia.db ]; then
  cp data/jadzia.db "data/jadzia.db.bak.$(date +%Y%m%d-%H%M%S)"
  echo "OK  DB backup"
fi

# Pull latest
git fetch origin
git reset --hard origin/master
echo "OK  git @ $(git log -1 --oneline)"

# .env production flags
grep -q '^JADZIA_ENV=' "$ENV_FILE" || echo 'JADZIA_ENV=production' >> "$ENV_FILE"
grep -q '^WEEKLY_BRIEF_INTERVAL_SECONDS=' "$ENV_FILE" \
  && sed -i 's/^WEEKLY_BRIEF_INTERVAL_SECONDS=.*/WEEKLY_BRIEF_INTERVAL_SECONDS=604800/' "$ENV_FILE" \
  || echo 'WEEKLY_BRIEF_INTERVAL_SECONDS=604800' >> "$ENV_FILE"

chown jadzia:jadzia "$ENV_FILE"
chmod 640 "$ENV_FILE"
echo "OK  .env flags (JADZIA_ENV, WEEKLY_BRIEF)"

# GA4 credentials readable by jadzia
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a
if [ -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" ] && [ -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
  chown jadzia:jadzia "$GOOGLE_APPLICATION_CREDENTIALS"
  chmod 640 "$GOOGLE_APPLICATION_CREDENTIALS"
  echo "OK  GA4 credentials permissions"
else
  echo "WARN GOOGLE_APPLICATION_CREDENTIALS missing or file not found: ${GOOGLE_APPLICATION_CREDENTIALS:-unset}"
fi

# venv + deps
if [ ! -x venv/bin/python ]; then
  rm -rf venv
  sudo -u jadzia python3 -m venv venv
fi
sudo -u jadzia venv/bin/python -m pip install --upgrade pip -q
if [ -f requirements.lock ]; then
  sudo -u jadzia venv/bin/python -m pip install -r requirements.lock -q
else
  sudo -u jadzia venv/bin/python -m pip install -r requirements.txt -q
fi
chown -R jadzia:jadzia "$JADZIA_ROOT"
echo "OK  venv deps"

# systemd
cp deployment/jadzia.service /etc/systemd/system/jadzia.service
systemctl daemon-reload
systemctl reset-failed jadzia 2>/dev/null || true
systemctl restart jadzia
sleep 8
echo "SERVICE: $(systemctl is-active jadzia)"

# Auth proof
CHAT_CODE=$(curl -s -o /dev/null -w '%{http_code}' -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"closure-proof","chat_id":"deploy-closure"}')
echo "CHAT_NO_AUTH: $CHAT_CODE"

# prod-smoke
set +e
bash deployment/prod-smoke.sh
SMOKE_EXIT=$?
set -e
echo "SMOKE_EXIT: $SMOKE_EXIT"

# analytics debug snippet
if [ -n "${JWT_SECRET:-}" ]; then
  TOKEN=$(JWT_SECRET="$JWT_SECRET" python3 -c 'import os,jwt; print(jwt.encode({"sub":"smoke"}, os.environ["JWT_SECRET"], algorithm="HS256"))')
  AN=$(curl -sS -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/analytics/snapshot?period=7d" | head -c 200)
  echo "ANALYTICS_SAMPLE: $AN"
fi

echo "=== Closure done ==="
