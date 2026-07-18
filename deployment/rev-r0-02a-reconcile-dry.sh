#!/bin/bash
set -euo pipefail
cd /opt/jadzia
sudo -u jadzia bash -lc 'source venv/bin/activate && PYTHONPATH=. python scripts/revenue_reconcile.py --db data/jadzia.db --output /tmp/rev-reconcile-dry.json'
python3 <<'PY'
import json
d = json.load(open("/tmp/rev-reconcile-dry.json", encoding="utf-8"))
print("mode", d["mode"])
print("history_preserved", d["history_preserved"])
print("summary", json.dumps(d["summary"]))
print("ga4_status", d["ga4_order_reconciliation"]["status"])
print("PASS dry-run reconcile")
PY
