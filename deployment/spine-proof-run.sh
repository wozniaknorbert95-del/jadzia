#!/usr/bin/env bash
# Spine proof runner — ON VPS /opt/jadzia
set -euo pipefail
cd /opt/jadzia
set -a
# shellcheck disable=SC1091
source .env
set +a

TOKEN=$(python3 -c 'import os,jwt; print(jwt.encode({"sub":"spine"}, os.environ["JWT_SECRET"], algorithm="HS256"))')
AUTH="Authorization: Bearer $TOKEN"

echo "=== BASELINE ==="
echo "service=$(systemctl is-active jadzia)"
echo "git_local=$(git rev-parse --short HEAD)"
echo "git_origin=$(git rev-parse --short origin/master 2>/dev/null || echo n/a)"
AUTH_CODE=$(curl -s -o /dev/null -w '%{http_code}' -X POST http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"proof","chat_id":"spine-proof"}')
echo "auth_post_chat_no_jwt=$AUTH_CODE"

echo "=== C1 orders ==="
sqlite3 data/jadzia.db "SELECT order_id FROM orders WHERE order_id != 'SMOKE-1' LIMIT 1;"

echo "=== C2 leads count ==="
sqlite3 data/jadzia.db "SELECT COUNT(*) FROM leads;"

echo "=== C3 analytics ==="
curl -sS -H "$AUTH" "http://127.0.0.1:8000/api/v1/analytics/snapshot?period=7d" | head -c 300
echo

echo "=== C4 calendar ==="
curl -sS -H "$AUTH" "http://127.0.0.1:8000/api/v1/content-calendar" | head -c 200
echo

echo "=== C5 widget ==="
curl -sS -X POST -H "Content-Type: application/json" -H "Origin: https://zzpackage.flexgrafik.nl" \
  -d '{"message":"Hoi, wat kost voertuigreclame?","session_id":"spine-proof"}' \
  "http://127.0.0.1:8000/api/v1/widget/chat" | head -c 300
echo

echo "=== C6 dry_run task ==="
./venv/bin/python3 scripts/send_task.py "TEST spine proof dry run only" --test_mode --dry_run --poll || true

echo "=== C7 weekly brief ==="
./venv/bin/python3 -c "from agent.nodes.brief_node import send_weekly_brief; print('brief_sent=', send_weekly_brief())"

echo "=== C9 dashboard ==="
curl -sS -H "$AUTH" "http://127.0.0.1:8000/worker/dashboard" | head -c 250
echo
echo "=== DONE ==="
