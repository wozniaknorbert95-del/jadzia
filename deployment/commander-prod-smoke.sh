#!/usr/bin/env bash
# COI Commander prod smoke — run ON VPS after deploy.
set -euo pipefail

BASE="${JADZIA_BASE_URL:-http://localhost:8000}"
PUB="${JADZIA_PUBLIC_URL:-https://api.zzpackage.flexgrafik.nl}"
ENV_FILE="${JADZIA_ENV_FILE:-/opt/jadzia/.env}"
PASS=0
FAIL=0

ok() { echo "OK  $1"; PASS=$((PASS + 1)); }
bad() { echo "FAIL $1"; FAIL=$((FAIL + 1)); }

echo "=== COI Commander prod smoke ==="
echo "commit=$(cd /opt/jadzia && git log -1 --format='%H %s')"

set -a
# shellcheck disable=SC1091
source "$ENV_FILE"
set +a

if [ -z "${JWT_SECRET:-}" ]; then
  bad "JWT_SECRET missing"
  echo "=== RESULT pass=$PASS fail=$FAIL ==="
  exit 1
fi

TOKEN=$(JWT_SECRET="$JWT_SECRET" python3 -c 'import os,jwt; print(jwt.encode({"sub":"deploy-smoke","role":"dowodca"}, os.environ["JWT_SECRET"], algorithm="HS256"))')
AUTH="Authorization: Bearer $TOKEN"

code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/commander/")
if [ "$code" = "200" ]; then ok "GET /commander/ local ($code)"; else bad "GET /commander/ local ($code)"; fi

code=$(curl -s -o /dev/null -w "%{http_code}" "$PUB/commander/")
if [ "$code" = "200" ]; then ok "GET /commander/ public ($code)"; else bad "GET /commander/ public ($code)"; fi

Q=$(curl -sS -H "$AUTH" "$BASE/api/v1/commander/queue")
if echo "$Q" | grep -q '"items"'; then ok "GET /api/v1/commander/queue"; else bad "GET /api/v1/commander/queue ($Q)"; fi

A=$(curl -sS -H "$AUTH" "$BASE/api/v1/agents")
if echo "$A" | grep -q '"agents"'; then ok "GET /api/v1/agents"; else bad "GET /api/v1/agents ($A)"; fi

T=$(curl -sS -X POST -H "$AUTH" \
  "$BASE/api/v1/commander/tickets?title=deploy%20smoke%20test&description=prod%20proof&base_url=${PUB}")
if echo "$T" | grep -q '"ticket_id"'; then ok "POST /api/v1/commander/tickets"; else bad "POST tickets ($T)"; fi

Q2=$(curl -sS -H "$AUTH" "$BASE/api/v1/commander/queue?severity=CRITICAL")
if echo "$Q2" | grep -q 'deploy smoke test\|wp_ticket\|ticket'; then ok "CRITICAL queue has ticket"; else bad "CRITICAL queue check ($Q2)"; fi

S=$(curl -sS -X PATCH -H "$AUTH" -H "Content-Type: application/json" \
  "$BASE/api/v1/commander/settings" \
  -d '{"delegat_email":"delegat@flexgrafik.nl"}')
if echo "$S" | grep -q 'delegat@flexgrafik.nl'; then ok "PATCH settings delegat_email"; else bad "PATCH settings ($S)"; fi

echo "=== RESULT pass=$PASS fail=$FAIL ==="
[ "$FAIL" -eq 0 ]
