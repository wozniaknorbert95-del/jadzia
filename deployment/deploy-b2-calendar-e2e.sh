#!/usr/bin/env bash
# Phase B.2 E2E: orders → suggestions → draft → pending_approval → Telegram alert
# Run ON VPS as root@185.243.54.115
set -euo pipefail

BASE="${JADZIA_BASE_URL:-http://localhost:8000}"
source /root/jadzia/.env
export JWT_SECRET

TOKEN=$(python3 -c 'import os,jwt; print(jwt.encode({"sub":"b2-e2e"}, os.environ["JWT_SECRET"], algorithm="HS256"))')
AUTH="Authorization: Bearer $TOKEN"

echo "=== Phase B.2 content-calendar E2E ==="

echo "--- Step 1: order suggestions ---"
SUG=$(curl -sS -H "$AUTH" "$BASE/api/v1/content-calendar/suggestions/orders?limit=5")
echo "$SUG" | python3 -m json.tool
ORDER_ID=$(echo "$SUG" | python3 -c '
import sys, json
orders = json.load(sys.stdin).get("orders", [])
if not orders:
    sys.exit(1)
# Prefer real WC order 3149 if present
for o in orders:
    if str(o.get("order_id")) == "3149":
        print("3149")
        sys.exit(0)
print(orders[0]["order_id"])
')
echo "Using source_order_id=$ORDER_ID"

echo "--- Step 2: POST draft ---"
CREATE=$(curl -sS -X POST -H "$AUTH" -H "Content-Type: application/json" \
  "$BASE/api/v1/content-calendar" \
  -d "{\"platform\":\"facebook\",\"title\":\"Case study order $ORDER_ID\",\"body_nl\":\"Klant succesverhaal van order $ORDER_ID.\",\"scheduled_at\":\"2026-07-01T10:00:00Z\",\"source_order_id\":\"$ORDER_ID\"}")
echo "$CREATE" | python3 -m json.tool
ENTRY_ID=$(echo "$CREATE" | python3 -c 'import sys,json; d=json.load(sys.stdin); assert d.get("sync_status")=="success"; print(d["entry_id"])')

echo "--- Step 3: PATCH pending_approval (triggers Telegram) ---"
PATCH=$(curl -sS -X PATCH -H "$AUTH" -H "Content-Type: application/json" \
  "$BASE/api/v1/content-calendar/$ENTRY_ID" \
  -d '{"status":"pending_approval"}')
echo "$PATCH" | python3 -m json.tool
STATUS=$(echo "$PATCH" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("status",""))')

if [ "$STATUS" = "pending_approval" ]; then
  echo "RESULT: PASS entry_id=$ENTRY_ID status=pending_approval (Telegram alert fired async)"
  exit 0
fi

echo "RESULT: FAIL status=$STATUS"
exit 1
