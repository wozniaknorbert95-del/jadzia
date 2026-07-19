#!/usr/bin/env bash
# Flip MB_MODE=propose on VPS — ONLY with explicit Dowódca GO.
# Usage: CONFIRM=GO_PROPOSE bash deployment/mkt-propose-cutover-vps.sh
# Does NOT deploy git; assumes tip already pulled. Does NOT enable Act.
set -euo pipefail

if [[ "${CONFIRM:-}" != "GO_PROPOSE" ]]; then
  echo "REFUSED: set CONFIRM=GO_PROPOSE after Dowódca ticket GO."
  echo "Preflight only: python scripts/mb_propose_preflight.py"
  exit 2
fi

cd /opt/jadzia
ENV_FILE="${ENV_FILE:-/opt/jadzia/.env}"
if [[ ! -f "$ENV_FILE" ]]; then
  echo "missing $ENV_FILE"
  exit 1
fi

if grep -qE '^MB_MODE=' "$ENV_FILE"; then
  sed -i 's/^MB_MODE=.*/MB_MODE=propose/' "$ENV_FILE"
else
  echo 'MB_MODE=propose' >> "$ENV_FILE"
fi

systemctl restart jadzia
sleep 2
systemctl is-active jadzia

TOKEN=$(sudo -u jadzia bash -lc 'cd /opt/jadzia && ./venv/bin/python3 scripts/jwt_token.py' | tail -n1 | tr -d '\r')
curl -sf "http://127.0.0.1:8000/api/v1/commander/marketing/shadow?limit=1" \
  -H "Authorization: Bearer ${TOKEN}" | python3 -c 'import sys,json;d=json.load(sys.stdin);print("mb_mode",d.get("mb_mode"))'
curl -sf "http://127.0.0.1:8000/api/v1/commander/marketing/breakers" \
  -H "Authorization: Bearer ${TOKEN}" | python3 -c 'import sys,json;d=json.load(sys.stdin);print("trips",[t.get("breaker_id") for t in d.get("trips")or[]])'

echo "=== PROPOSE_CUTOVER_ENV_OK (Act still token-gated) ==="
