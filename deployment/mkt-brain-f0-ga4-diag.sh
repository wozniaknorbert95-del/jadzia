#!/bin/bash
set -euo pipefail
python3 - <<'PY'
import json
d=json.load(open("/tmp/dtl-ingest.json"))
for s in d.get("steps") or []:
    if s.get("source") == "ga4":
        print("ga4_step", s)
print("quality", d.get("quality"))
PY
sudo -u jadzia bash -lc 'cd /opt/jadzia && ./venv/bin/python3 - <<"PY"
from core.ga4_client import is_ga4_configured, get_property_id_zzpackage, get_property_id_app
print("ga4_configured", is_ga4_configured())
print("prop_zz", bool(get_property_id_zzpackage()))
print("prop_app", bool(get_property_id_app()))
PY'
