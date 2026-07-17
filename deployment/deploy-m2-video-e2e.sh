#!/usr/bin/env bash
# M2 E2E: video content_type → GDrive media_url → POST publish → publish-status
# Run ON VPS as jadzia — requires FB_* in .env and M2_TEST_GDRIVE_URL (public MP4 share link)
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
if [[ -z "${M2_TEST_GDRIVE_URL:-}" ]]; then
  echo "FAIL: set M2_TEST_GDRIVE_URL to a public Drive MP4 share link"
  echo "Example: export M2_TEST_GDRIVE_URL='https://drive.google.com/file/d/FILE_ID/view'"
  exit 1
fi

export JWT_SECRET

TOKEN=$(python3 -c 'import os,jwt; print(jwt.encode({"sub":"m2-e2e"}, os.environ["JWT_SECRET"], algorithm="HS256"))')
AUTH="Authorization: Bearer $TOKEN"
TS=$(date -u +%Y%m%dT%H%M%SZ)
MEDIA_JSON=$(python3 -c 'import json,os; print(json.dumps(os.environ["M2_TEST_GDRIVE_URL"]))')

echo "=== M2 Facebook video publish E2E ==="
echo "Page ID: $FB_PAGE_ID"

echo "--- Step 1: POST video draft ---"
CREATE=$(curl -sS -X POST -H "$AUTH" -H "Content-Type: application/json" \
  "$BASE/api/v1/content-calendar" \
  -d "{\"platform\":\"facebook\",\"title\":\"M2 video E2E $TS\",\"body_nl\":\"Jadzia M2 video test $TS — safe to delete.\",\"scheduled_at\":\"2026-08-01T09:00:00Z\",\"scheduled_publish_at\":\"2026-08-01T09:00:00Z\",\"content_type\":\"video\",\"media_url\":$MEDIA_JSON,\"status\":\"draft\"}")
echo "$CREATE" | python3 -m json.tool
ENTRY_ID=$(echo "$CREATE" | python3 -c 'import sys,json; d=json.load(sys.stdin); assert d.get("sync_status")=="success", d; print(d["entry_id"])')

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

echo "=== PASS === entry_id=$ENTRY_ID fb_post_id=$FB_POST_ID content_type=video"
echo "Manual: verify video on FlexGrafik Facebook page, then delete test post if desired."
