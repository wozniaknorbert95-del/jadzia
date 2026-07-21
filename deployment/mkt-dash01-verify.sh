#!/bin/bash
set -euo pipefail
cd /opt/jadzia
echo "TIP=$(git rev-parse --short HEAD)"
systemctl is-active jadzia
TOKEN="$(sudo -u jadzia bash -lc 'cd /opt/jadzia && ./venv/bin/python3 scripts/jwt_token.py' | tail -n1 | tr -d '\r')"

echo "=== fb-health ==="
curl -sf "http://127.0.0.1:8000/api/v1/commander/marketing/fb-health" \
  -H "Authorization: Bearer ${TOKEN}" \
  | python3 -c 'import sys,json;d=json.load(sys.stdin);print("ok",d.get("ok"),"has_read_insights",d.get("has_read_insights"),"msg",(d.get("message_pl") or "")[:100])'

echo "=== weekly-draft ==="
curl -sf "http://127.0.0.1:8000/api/v1/commander/marketing/weekly-draft" \
  -H "Authorization: Bearer ${TOKEN}" \
  | python3 -c 'import sys,json;d=json.load(sys.stdin);k=d.get("kpis") or {};print("week",d.get("iso_week"),"leads",k.get("leads"),"spend",k.get("spend_eur"),"cpl",k.get("cpl"),"decision",d.get("decision"))'

echo "=== data-health ==="
curl -sf "http://127.0.0.1:8000/api/v1/commander/marketing/data-health" \
  -H "Authorization: Bearer ${TOKEN}" \
  | python3 -c 'import sys,json;d=json.load(sys.stdin);print("overall",d.get("overall_status"));print("parks",[p.get("id") for p in (d.get("conscious_parks") or [])]);print("organic",d.get("facebook_organic"));print("drivers_n",len(d.get("drivers") or []))'

echo "=== static ==="
grep -c 'mkt-dash03' commander-ui/index.html || true
grep -c 'has_read_insights' commander-ui/app.js || true
grep -c 'weekly-draft-panel' commander-ui/index.html || true
grep -c 'dtl-parks' commander-ui/index.html || true
grep -c 'H-Insights' commander-ui/index.html || true
grep -c '/worker/health' commander-ui/app.js || true
test -f commander-ui/app.js && test -f commander-ui/styles.css
echo "=== design-agent health ==="
curl -sf "http://127.0.0.1:8000/api/v1/design-agent/health" \
  | python3 -c 'import sys,json;d=json.load(sys.stdin);print("status",d.get("status"),"service",d.get("service"))'
echo "=== worker health ==="
curl -sf "http://127.0.0.1:8000/worker/health" \
  | python3 -c 'import sys,json;d=json.load(sys.stdin);print("status",d.get("status"),"ssh",d.get("ssh_connection"))'
echo "=== VERIFY_OK ==="
