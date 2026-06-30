#!/usr/bin/env bash
# GA4 zzpackage verify — run ON VPS after SA Viewer grant on property 528785553.
set -euo pipefail

source /root/jadzia/.env
export JWT_SECRET

TOKEN=$(python3 -c 'import os,jwt; print(jwt.encode({"sub":"ga4-verify"}, os.environ["JWT_SECRET"], algorithm="HS256"))')

echo "=== GA4 snapshot (period=7d) ==="
RESP=$(curl -sS -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/analytics/snapshot?period=7d")

echo "$RESP" | python3 -m json.tool

SYNC=$(echo "$RESP" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("sync_status",""))')
ZZ=$(echo "$RESP" | python3 -c 'import sys,json; d=json.load(sys.stdin); print("present" if d.get("sources",{}).get("zzpackage") else "missing")')
ERR=$(echo "$RESP" | python3 -c 'import sys,json; print(len(json.load(sys.stdin).get("errors",[])))')

if [ "$SYNC" = "success" ] && [ "$ZZ" = "present" ] && [ "$ERR" = "0" ]; then
  echo "RESULT: PASS (sync_status=success, sources.zzpackage present, errors=0)"
  exit 0
fi

echo "RESULT: FAIL sync_status=$SYNC zzpackage=$ZZ errors_count=$ERR"
exit 1
