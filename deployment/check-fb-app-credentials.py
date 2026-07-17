#!/usr/bin/env python3
"""Boolean check for FB env keys — never prints secret values."""
from pathlib import Path

env = Path(__file__).resolve().parent.parent / ".env"
keys: dict[str, bool] = {}
if env.is_file():
    for line in env.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        keys[k.strip()] = bool(v.strip().strip('"').strip("'"))

for k in ("FB_PAGE_ID", "FB_ACCESS_TOKEN", "FB_APP_ID", "FB_APP_SECRET"):
    print(f"{k}={'SET' if keys.get(k) else 'MISSING'}")

if keys.get("FB_APP_ID") and keys.get("FB_APP_SECRET"):
    print("APP_CREDENTIALS_OK")
else:
    print("APP_CREDENTIALS_MISSING")
