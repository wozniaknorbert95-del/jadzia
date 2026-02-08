#!/bin/bash
# Run on VPS: bash diagnose_telegram_session.sh
# Diagnoses why new Telegram tasks may not appear in session state.

DB="${DB:-/root/jadzia/data/jadzia.db}"
CHAT="telegram_6746343970"
SOURCE="telegram"

echo "=== 1. Newest task for telegram session ==="
sqlite3 "$DB" "SELECT task_id, status, created_at FROM tasks WHERE chat_id='$CHAT' AND source='$SOURCE' ORDER BY created_at DESC LIMIT 1;"

echo ""
echo "=== 2. Session state (active_task_id, task_queue) ==="
sqlite3 "$DB" "SELECT active_task_id, task_queue FROM sessions WHERE chat_id='$CHAT' AND source='$SOURCE';"

echo ""
echo "=== 3. Last 20 worker loop lines for this chat ==="
tail -200 /root/jadzia/logs/jadzia.log 2>/dev/null | grep "$CHAT" | tail -20

echo ""
echo "=== 4. Recent POST /worker/task or worker_create_task (last 50 lines) ==="
tail -300 /root/jadzia/logs/jadzia.log 2>/dev/null | grep -E "worker_create_task|POST.*worker/task" | tail -10
