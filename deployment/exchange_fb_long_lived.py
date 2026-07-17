#!/usr/bin/env python3
"""Exchange short-lived User token for long-lived User token via Meta oauth."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import requests

_root = Path(__file__).resolve().parent.parent
FACEBOOK_API_VERSION = "v25.0"
FACEBOOK_BASE = f"https://graph.facebook.com/{FACEBOOK_API_VERSION}"


def load_env_file(path: Path | None = None) -> None:
    env_path = path or (_root / ".env")
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        os.environ.setdefault(key.strip(), val.strip())


def exchange_long_lived_user_token(
    short_token: str,
    *,
    app_id: str | None = None,
    app_secret: str | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """
    Short-lived USER → long-lived USER (~60 days).

    Returns dict with status success|error|skipped.
    On success: access_token, expires_in (seconds, optional).
    """
    token = (short_token or "").strip()
    client_id = (app_id or os.environ.get("FB_APP_ID") or "").strip()
    client_secret = (app_secret or os.environ.get("FB_APP_SECRET") or "").strip()

    if not token:
        return {"status": "error", "message": "missing access token"}
    if not client_id or not client_secret:
        return {
            "status": "skipped",
            "message": "FB_APP_ID / FB_APP_SECRET not set — long-lived exchange skipped",
        }

    try:
        resp = requests.get(
            f"{FACEBOOK_BASE}/oauth/access_token",
            params={
                "grant_type": "fb_exchange_token",
                "client_id": client_id,
                "client_secret": client_secret,
                "fb_exchange_token": token,
            },
            timeout=timeout,
        )
        data = resp.json() if resp.content else {}
        if resp.status_code >= 400:
            return {
                "status": "error",
                "message": "fb_exchange_token failed",
                "details": data,
                "http_status": resp.status_code,
            }
        access = data.get("access_token")
        if not access:
            return {"status": "error", "message": "no access_token in exchange response", "details": data}
        return {
            "status": "success",
            "access_token": access,
            "expires_in": data.get("expires_in"),
            "token_type": data.get("token_type"),
        }
    except requests.RequestException as exc:
        return {"status": "error", "message": str(exc)}


def main() -> int:
    load_env_file()
    token = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("FB_ACCESS_TOKEN", "")).strip()
    result = exchange_long_lived_user_token(token)
    # Never print full token on CLI — callers import the function for the value
    safe = {k: v for k, v in result.items() if k != "access_token"}
    if result.get("status") == "success":
        safe["access_token_len"] = len(result["access_token"])
    print(json.dumps(safe, ensure_ascii=False))
    if result.get("status") == "success":
        return 0
    return 0 if result.get("status") == "skipped" else 1


if __name__ == "__main__":
    raise SystemExit(main())
