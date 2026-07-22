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
grep -c 'mkt-dash06' commander-ui/index.html || true
grep -c 'has_read_insights' commander-ui/app.js || true
grep -c 'weekly-draft-panel' commander-ui/index.html || true
grep -c 'dtl-parks' commander-ui/index.html || true
grep -c 'mkt-decision-rail' commander-ui/index.html || true
grep -c 'home-ops-rail' commander-ui/index.html || true
grep -c 'ai-os-map' commander-ui/index.html || true
grep -c 'analytics-kpi-tiles' commander-ui/index.html || true
grep -c 'more-sheet' commander-ui/index.html || true
grep -c 'phase-c-cards' commander-ui/index.html || true
grep -c 'sev-chip' commander-ui/styles.css || true
grep -c 'propose-preflight' commander-ui/app.js || true
grep -c 'actions/execute' commander-ui/app.js || true
grep -c 'H-Meta' commander-ui/index.html || true
grep -c '/worker/health' commander-ui/app.js || true
test -f commander-ui/app.js && test -f commander-ui/styles.css
echo "=== mb-rail apis (auth required; expect 401 without token ok) ==="
for p in propose-preflight breakers shadow/accuracy brain-bus memory/status; do
  code=$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:8000/api/v1/commander/marketing/${p}" || true)
  echo "${p} ${code}"
done
echo "=== mb-rail with JWT ==="
curl -sf "http://127.0.0.1:8000/api/v1/commander/marketing/propose-preflight" \
  -H "Authorization: Bearer ${TOKEN}" \
  | python3 -c 'import sys,json;d=json.load(sys.stdin);print("verdict",d.get("verdict"),"mode",d.get("mb_mode"))'
curl -sf "http://127.0.0.1:8000/api/v1/commander/marketing/shadow/accuracy" \
  -H "Authorization: Bearer ${TOKEN}" \
  | python3 -c 'import sys,json;d=json.load(sys.stdin);print("accuracy",d.get("accuracy"),"gate",d.get("gate_ready"),"n",d.get("n_scored"))'
curl -sf "http://127.0.0.1:8000/api/v1/commander/marketing/breakers" \
  -H "Authorization: Bearer ${TOKEN}" \
  | python3 -c 'import sys,json;d=json.load(sys.stdin);print("allowed",d.get("allowed"),"trips",[t.get("breaker_id") for t in (d.get("trips") or [])])'
curl -sf "http://127.0.0.1:8000/api/v1/agents" \
  -H "Authorization: Bearer ${TOKEN}" \
  | python3 -c 'import sys,json;d=json.load(sys.stdin);a=(d.get("agents") or [{}])[0];print("agent0",a.get("agent_id"),"next",a.get("next_expected_run"),"sla",a.get("sla_ok"))'
echo "=== design-agent health ==="
curl -sf "http://127.0.0.1:8000/api/v1/design-agent/health" \
  | python3 -c 'import sys,json;d=json.load(sys.stdin);print("status",d.get("status"),"service",d.get("service"))'
echo "=== worker health ==="
curl -sf "http://127.0.0.1:8000/worker/health" \
  | python3 -c 'import sys,json;d=json.load(sys.stdin);print("status",d.get("status"),"ssh",d.get("ssh_connection"))'
echo "=== VERIFY_OK ==="
