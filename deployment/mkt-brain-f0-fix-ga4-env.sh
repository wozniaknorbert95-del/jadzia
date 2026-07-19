#!/bin/bash
# Restore GA4 env on VPS from known INT-009 values + existing SA file.
# Does not print secret contents.
set -euo pipefail

ENV=/opt/jadzia/.env
CRED_CANDIDATES=(
  /opt/jadzia/secrets/ga4-service-account.json
  /root/jadzia/secrets/ga4-service-account.json
  /opt/jadzia/ga4-service-account.json
  /root/jadzia-backup-20260630-062926/secrets/ga4-service-account.json
)

echo "=== locate SA json ==="
CRED=""
for p in "${CRED_CANDIDATES[@]}"; do
  if [ -f "$p" ]; then
    CRED="$p"
    echo "found=$p size=$(wc -c < "$p")"
    break
  fi
  echo "missing=$p"
done

if [ -z "$CRED" ]; then
  echo "SEARCH deeper..."
  FOUND="$(find /opt/jadzia /root/jadzia -maxdepth 4 -type f -name '*ga4*service*.json' 2>/dev/null | head -5 || true)"
  echo "$FOUND"
  CRED="$(echo "$FOUND" | head -1)"
fi

if [ -z "${CRED}" ] || [ ! -f "${CRED}" ]; then
  echo "ABORT no GA4 service account json on disk"
  exit 2
fi

# Ensure canonical path for jadzia user
mkdir -p /opt/jadzia/secrets
if [ "$CRED" != "/opt/jadzia/secrets/ga4-service-account.json" ]; then
  cp -n "$CRED" /opt/jadzia/secrets/ga4-service-account.json || cp "$CRED" /opt/jadzia/secrets/ga4-service-account.json
  CRED=/opt/jadzia/secrets/ga4-service-account.json
fi
chown jadzia:jadzia "$CRED"
chmod 640 "$CRED"
echo "cred_canonical=$CRED"

upsert_env() {
  local key="$1" val="$2"
  if grep -q "^${key}=" "$ENV" 2>/dev/null; then
    sed -i "s|^${key}=.*|${key}=${val}|" "$ENV"
    echo "updated=${key}"
  else
    echo "${key}=${val}" >> "$ENV"
    echo "added=${key}"
  fi
}

# Property IDs from INT-009 proof (docs/archive/handoffs/2026-06-26-deploy-int-009-proof.md)
upsert_env GOOGLE_APPLICATION_CREDENTIALS "$CRED"
upsert_env GA4_PROPERTY_ID_APP "528764186"
upsert_env GA4_PROPERTY_ID_ZZPACKAGE "528785553"

echo "=== env names set ==="
grep -E '^(GOOGLE_APPLICATION_CREDENTIALS|GA4_PROPERTY_ID_)' "$ENV" | sed 's/=.*/=***/'

echo "=== systemd unit EnvironmentFile? ==="
systemctl cat jadzia | grep -E 'EnvironmentFile|WorkingDirectory|User=' || true

echo "=== restart + runtime check ==="
systemctl restart jadzia
sleep 5
systemctl is-active jadzia
curl -sf http://127.0.0.1:8000/health
echo

sudo -u jadzia bash -lc 'cd /opt/jadzia && ./venv/bin/python3 - <<"PY"
from dotenv import load_dotenv
load_dotenv("/opt/jadzia/.env", override=True)
from core.ga4_client import is_ga4_configured, get_property_id_app, get_property_id_zzpackage
print("ga4_configured", is_ga4_configured())
print("prop_app_set", bool(get_property_id_app()))
print("prop_zz_set", bool(get_property_id_zzpackage()))
PY'

echo "=== re-ingest ==="
TOKEN="$(sudo -u jadzia bash -lc 'cd /opt/jadzia && ./venv/bin/python3 scripts/jwt_token.py' | tail -n1 | tr -d '\r')"
curl -sf -X POST http://127.0.0.1:8000/api/v1/commander/marketing/dtl/ingest \
  -H "Authorization: Bearer ${TOKEN}" \
  -H 'Content-Type: application/json' \
  -d '{}' \
  -o /tmp/dtl-ingest2.json

python3 - <<'PY'
import json
d=json.load(open("/tmp/dtl-ingest2.json"))
print("steps_ok", d.get("steps_ok"), "steps_error", d.get("steps_error"))
for s in d.get("steps") or []:
    print(" step", s.get("source"), s.get("status"), s.get("sync_status",""), "facts=", s.get("facts_written", s.get("written","")))
PY

curl -sf http://127.0.0.1:8000/api/v1/commander/marketing/data-health \
  -H "Authorization: Bearer ${TOKEN}" \
  -o /tmp/dtl-health2.json
python3 - <<'PY'
import json
d=json.load(open("/tmp/dtl-health2.json"))
print("overall", d.get("overall_status"))
print("quality", d.get("quality_summary"))
ga4=d.get("freshness",{}).get("ga4",{})
print("ga4_freshness", ga4.get("status"), ga4.get("ingest_status"), ga4.get("last_sync_at"))
PY

echo "=== FIX_GA4_DONE ==="
