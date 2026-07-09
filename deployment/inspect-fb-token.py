#!/usr/bin/env python3
"""Inspect FB token type (no secrets printed)."""
import os
import sys
from pathlib import Path

import requests

_root = Path(__file__).resolve().parent.parent
_env = _root / ".env"
if _env.exists():
    for line in _env.read_text(encoding="utf-8").splitlines():
        if line.startswith("FB_ACCESS_TOKEN="):
            os.environ["FB_ACCESS_TOKEN"] = line.split("=", 1)[1].strip()
        if line.startswith("FB_PAGE_ID="):
            os.environ["FB_PAGE_ID"] = line.split("=", 1)[1].strip()

tok = os.environ.get("FB_ACCESS_TOKEN", "")
page_id = os.environ.get("FB_PAGE_ID", "")
if not tok:
    print("error: no FB_ACCESS_TOKEN", file=sys.stderr)
    sys.exit(1)

base = "https://graph.facebook.com/v25.0"
for ep, fields in [("me", "id,name,category"), ("debug_token", "data{type,expires_at,scopes}")]:
    params = {"access_token": tok, "fields": fields} if fields != "data{type,expires_at,scopes}" else {"input_token": tok, "access_token": tok}
    if ep == "debug_token":
        params = {"input_token": tok, "access_token": tok}
    else:
        params = {"access_token": tok, "fields": fields}
    r = requests.get(f"{base}/{ep}", params=params, timeout=20)
    print(f"{ep}: {r.status_code}")
    print(r.text[:600])

if page_id:
    r = requests.get(f"{base}/{page_id}", params={"access_token": tok, "fields": "id,name"}, timeout=20)
    print(f"page_check: {r.status_code}")
    print(r.text[:300])
