#!/usr/bin/env python3
"""Exchange User token for Page Access Token and save to .env."""
import json
import os
import re
import sys
from pathlib import Path

import requests

_root = Path(__file__).resolve().parent.parent
_env = _root / ".env"


def _load_env() -> None:
    if not _env.exists():
        return
    for line in _env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        os.environ.setdefault(key.strip(), val.strip())


def _save_token(token: str) -> None:
    text = _env.read_text(encoding="utf-8")
    line = f"FB_ACCESS_TOKEN={token}"
    if re.search(r"^FB_ACCESS_TOKEN=", text, re.MULTILINE):
        text = re.sub(r"^FB_ACCESS_TOKEN=.*$", line, text, count=1, flags=re.MULTILINE)
    else:
        if text and not text.endswith("\n"):
            text += "\n"
        text += line + "\n"
    _env.write_text(text, encoding="utf-8")


def main() -> int:
    _load_env()
    user_token = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("FB_ACCESS_TOKEN", "")).strip()
    page_id = os.environ.get("FB_PAGE_ID", "").strip()
    if not user_token or not page_id:
        print(json.dumps({"status": "error", "message": "need FB_ACCESS_TOKEN and FB_PAGE_ID"}))
        return 1

    base = "https://graph.facebook.com/v25.0"
    resp = requests.get(
        f"{base}/{page_id}",
        params={"fields": "access_token,name", "access_token": user_token},
        timeout=30,
    )
    if resp.status_code >= 400:
        resp = requests.get(
            f"{base}/me/accounts",
            params={"access_token": user_token, "fields": "id,name,access_token"},
            timeout=30,
        )
    data = resp.json()
    if resp.status_code >= 400:
        print(json.dumps({"status": "error", "message": "graph error", "details": data}, ensure_ascii=False))
        return 1

    page_token = data.get("access_token")
    if not page_token and "data" in data:
        for page in data["data"]:
            if str(page.get("id")) == page_id:
                page_token = page.get("access_token")
                break

    if not page_token:
        print(json.dumps({"status": "error", "message": "no page token in response", "details": data}, ensure_ascii=False))
        return 1

    _save_token(page_token)
    check = requests.get(
        f"{base}/debug_token",
        params={"input_token": page_token, "access_token": page_token},
        timeout=20,
    ).json()
    token_type = (check.get("data") or {}).get("type")
    print(json.dumps({
        "status": "success",
        "page_id": page_id,
        "page_name": data.get("name"),
        "token_type": token_type,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
