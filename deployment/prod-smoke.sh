#!/usr/bin/env bash
# Prod smoke suite — run ON VPS (jadzia@/opt/jadzia after OPS-01).
# Usage: bash deployment/prod-smoke.sh

set -euo pipefail

BASE="${JADZIA_BASE_URL:-http://localhost:8000}"
JADZIA_ROOT="${JADZIA_ROOT:-/opt/jadzia}"
ENV_FILE="${JADZIA_ENV_FILE:-${JADZIA_ROOT}/.env}"
DB_PATH="${JADZIA_DB_PATH:-${JADZIA_ROOT}/data/jadzia.db}"
PASS=0
FAIL=0

ok() { echo "OK  $1"; PASS=$((PASS + 1)); }
bad() { echo "FAIL $1"; FAIL=$((FAIL + 1)); }

echo "=== Jadzia prod smoke ==="
echo "base=$BASE"

if curl -sf "$BASE/worker/health" | grep -q '"status"'; then
  ok "worker/health"
else
  bad "worker/health"
fi

if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$ENV_FILE"
  set +a
fi

if [ -z "${JWT_SECRET:-}" ]; then
  bad "JWT_SECRET missing — skip authed routes"
else
  TOKEN=$(JWT_SECRET="$JWT_SECRET" python3 -c 'import os,jwt; print(jwt.encode({"sub":"smoke"}, os.environ["JWT_SECRET"], algorithm="HS256"))')
  AUTH="Authorization: Bearer $TOKEN"

  AN=$(curl -sS -H "$AUTH" "$BASE/api/v1/analytics/snapshot?period=7d")
  if echo "$AN" | grep -qE '"sync_status":"(success|degraded)"'; then
    ok "analytics/snapshot"
  else
    bad "analytics/snapshot"
  fi

  CC=$(curl -sS -H "$AUTH" "$BASE/api/v1/content-calendar")
  if echo "$CC" | grep -q '"total"'; then
    ok "content-calendar list"
  else
    bad "content-calendar list"
  fi

  CR=$(curl -sS -X POST -H "$AUTH" -H "Content-Type: application/json" \
    "$BASE/api/v1/content-calendar" \
    -d '{"platform":"facebook","title":"Smoke test","body_nl":"Prod smoke entry","scheduled_at":"2026-12-01T10:00:00Z"}')
  if echo "$CR" | grep -q '"sync_status":"success"'; then
    ok "content-calendar create"
  else
    bad "content-calendar create"
  fi
fi

if [ -n "${WC_WEBHOOK_SECRET:-}" ]; then
  ok "WC_WEBHOOK_SECRET configured"
else
  bad "WC_WEBHOOK_SECRET missing"
fi

if [ -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" ] && [ -n "${GA4_PROPERTY_ID_APP:-}" ]; then
  ok "GA4 env configured"
else
  echo "WARN GA4 not configured — DEPLOY-03 pending"
fi

if [ -n "${FB_PAGE_ID:-}" ] && [ -n "${FB_ACCESS_TOKEN:-}" ]; then
  ok "Facebook publish env configured"
else
  echo "WARN FB_PAGE_ID/FB_ACCESS_TOKEN missing — B3 E2E pending"
fi

ORDERS=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM orders;" 2>/dev/null || echo 0)
echo "INFO orders count=$ORDERS"
if sqlite3 "$DB_PATH" "SELECT order_id FROM orders WHERE order_id != 'SMOKE-1' LIMIT 1;" 2>/dev/null | grep -q .; then
  ok "real WC order present"
else
  echo "WARN only SMOKE-1 — DEPLOY-01 Mollie E2E pending"
fi

echo "=== RESULT pass=$PASS fail=$FAIL ==="
[ "$FAIL" -eq 0 ]
