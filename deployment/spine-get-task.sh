#!/usr/bin/env bash
set -euo pipefail
cd /opt/jadzia
set -a
# shellcheck disable=SC1091
source .env
set +a
T=$(./venv/bin/python3 scripts/jwt_token.py)
TASK_ID="${1:-0908f7c3-f130-42eb-99c7-ca3267222c45}"
curl -sS -H "Authorization: Bearer $T" "http://127.0.0.1:8000/worker/task/$TASK_ID"
