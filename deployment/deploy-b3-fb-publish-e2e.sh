#!/usr/bin/env bash
# Phase B.3 E2E: draft → approved → POST publish → publish-status (INT-011)
# Run ON VPS as jadzia@185.243.54.115 — requires FB_PAGE_ID + FB_ACCESS_TOKEN in .env
set -euo pipefail

BASE="${JADZIA_BASE_URL:-http://localhost:8000}"
ENV_FILE="${JADZIA_ENV_FILE:-/opt/jadzia/.env}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "FAIL: missing $ENV_FILE"
  exit 1
fi

# shellcheck source=/dev/null
source "$ENV_FILE"

if [[ -z "${JWT_SECRET:-}" ]]; then
  echo "FAIL: JWT_SECRET not set in $ENV_FILE"
  exit 1
fi
if [[ -z "${FB_PAGE_ID:-}" || -z "${FB_ACCESS_TOKEN:-}" ]]; then
  echo "FAIL: FB_PAGE_ID and FB_ACCESS_TOKEN required in $ENV_FILE"
  exit 1
fi

export JWT_SECRET

TOKEN=$(python3 -c 'import os,jwt; print(jwt.encode({"sub":"b3-e2e"}, os.environ["JWT_SECRET"], algorithm="HS256"))')
AUTH="Authorization: Bearer $TOKEN"
TS=$(date -u +%Y%m%dT%H%M%SZ)

echo "=== Phase B.3 Facebook publish E2E ==="
echo "Page ID: $FB_PAGE_ID"

echo "--- Step 1: POST draft (test post) ---"
CREATE=$(curl -sS -X POST -H "$AUTH" -H "Content-Type: application/json" \
  "$BASE/api/v1/content-calendar" \
  -d "{\"platform\":\"facebook\",\"title\":\"B3 E2E $TS\",\"body_nl\":\"Jadzia COI test $TS — safe to delete.\",\"scheduled_at\":\"2026-08-01T09:00:00Z\"}")
echo "$CREATE" | python3 -m json.tool
ENTRY_ID=$(echo "$CREATE" | python3 -c 'import sys,json; d=json.load(sys.stdin); assert d.get("sync_status")=="success"; print(d["entry_id"])')

echo "--- Step 2: PATCH approved ---"
curl -sS -X PATCH -H "$AUTH" -H "Content-Type: application/json" \
  "$BASE/api/v1/content-calendar/$ENTRY_ID" \
  -d '{"status":"approved"}' | python3 -m json.tool

echo "--- Step 3: POST publish ---"
PUB=$(curl -sS -X POST -H "$AUTH" \
  "$BASE/api/v1/content-calendar/$ENTRY_ID/publish")
echo "$PUB" | python3 -m json.tool
FB_POST_ID=$(echo "$PUB" | python3 -c 'import sys,json; d=json.load(sys.stdin); assert d.get("status")=="success", d; print(d["post_id"])')

echo "--- Step 4: GET publish-status ---"
STATUS=$(curl -sS -H "$AUTH" \
  "$BASE/api/v1/content-calendar/$ENTRY_ID/publish-status")
echo "$STATUS" | python3 -m json.tool
echo "$STATUS" | python3 -c 'import sys,json; d=json.load(sys.stdin); assert d.get("status")=="published"; assert d.get("fb_post_id")'

echo "=== PASS === entry_id=$ENTRY_ID fb_post_id=$FB_POST_ID"
echo "Manual: verify post on FlexGrafik Facebook page, then delete test post if desired."
