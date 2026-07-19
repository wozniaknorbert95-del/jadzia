#!/bin/bash
# MKT-BRAIN-PRO F0 — post-deploy verify on VPS
set -euo pipefail

cd /opt/jadzia
SHORT="$(git rev-parse --short HEAD)"
echo "tip=${SHORT}"
test "${SHORT}" = "f28a938"

echo "=== health ==="
curl -sf http://127.0.0.1:8000/health
echo
systemctl is-active jadzia

echo "=== mint JWT ==="
TOKEN="$(sudo -u jadzia bash -lc 'cd /opt/jadzia && ./venv/bin/python3 scripts/jwt_token.py' | tail -n1 | tr -d '\r')"
test -n "${TOKEN}"

echo "=== DTL ingest POST ==="
curl -sf -X POST http://127.0.0.1:8000/api/v1/commander/marketing/dtl/ingest \
  -H "Authorization: Bearer ${TOKEN}" \
  -H 'Content-Type: application/json' \
  -d '{}' \
  -o /tmp/dtl-ingest.json
python3 - <<'PY'
import json
d=json.load(open("/tmp/dtl-ingest.json"))
print("steps_ok", d.get("steps_ok"))
print("steps_error", d.get("steps_error"))
for s in d.get("steps") or []:
    print(" step", s.get("source"), s.get("status"),
          "written="+str(s.get("written", s.get("facts_written", ""))))
assert int(d.get("steps_ok") or 0) >= 4, "expected >=4 ok steps"
PY

echo "=== data-health GET ==="
curl -sf http://127.0.0.1:8000/api/v1/commander/marketing/data-health \
  -H "Authorization: Bearer ${TOKEN}" \
  -o /tmp/dtl-health.json
python3 - <<'PY'
import json
d=json.load(open("/tmp/dtl-health.json"))
print("overall", d.get("overall_status"))
print("margin", d.get("margin_coverage"))
print("quality", d.get("quality_summary"))
print("freshness_keys", sorted((d.get("freshness") or {}).keys()))
facts=d.get("recent_facts") or []
print("recent_facts", len(facts))
assert d.get("panel") == "data_health"
assert "freshness" in d
assert "margin_coverage" in d
assert len(facts) >= 1, "expected facts after ingest"
PY

echo "=== sqlite counts ==="
sudo -u jadzia sqlite3 /opt/jadzia/data/jadzia.db \
  "SELECT 'raw', COUNT(*) FROM marketing_raw_ingest
   UNION ALL SELECT 'facts', COUNT(*) FROM marketing_facts
   UNION ALL SELECT 'flags_active', COUNT(*) FROM data_quality_flags WHERE active=1
   UNION ALL SELECT 'margin', COUNT(*) FROM order_margin_facts;"

echo "=== VERIFY_OK @ ${SHORT} ==="
