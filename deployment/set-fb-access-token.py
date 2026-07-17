#!/usr/bin/env python3
"""Update FB_ACCESS_TOKEN in .env; long-lived USER exchange + USER → PAGE when needed."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
env_path = _root / ".env"


def _load_env_into_os() -> None:
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        os.environ[key.strip()] = val.strip()


def _save_token(token: str) -> None:
    text = env_path.read_text(encoding="utf-8")
    line = f"FB_ACCESS_TOKEN={token}"
    if re.search(r"^FB_ACCESS_TOKEN=", text, re.MULTILINE):
        text = re.sub(r"^FB_ACCESS_TOKEN=.*$", line, text, count=1, flags=re.MULTILINE)
    else:
        if text and not text.endswith("\n"):
            text += "\n"
        text += line + "\n"
    env_path.write_text(text, encoding="utf-8")
    os.environ["FB_ACCESS_TOKEN"] = token


def main() -> int:
    token = (sys.argv[1] if len(sys.argv) > 1 else "").strip()
    if not token:
        print("usage: set-fb-access-token.py <access_token>", file=sys.stderr)
        return 1

    if not env_path.exists():
        print(f"error: missing {env_path}", file=sys.stderr)
        return 1

    _save_token(token)
    _load_env_into_os()

    sys.path.insert(0, str(_root))
    from agent.publishers.facebook import check_token_health
    from deployment.exchange_fb_long_lived import exchange_long_lived_user_token

    long_lived_meta: dict = {"status": "not_attempted"}
    health = check_token_health()

    # Long-lived exchange unless we already have a healthy PAGE token
    if not (health.get("ok") and health.get("token_type") == "PAGE"):
        long_lived_meta = exchange_long_lived_user_token(token)
        if long_lived_meta.get("status") == "success":
            _save_token(long_lived_meta["access_token"])
            print(
                "info: exchanged short-lived → long-lived USER token "
                f"(expires_in={long_lived_meta.get('expires_in')})",
                file=sys.stderr,
            )
            health = check_token_health()
        elif long_lived_meta.get("status") == "skipped":
            print(f"warn: {long_lived_meta.get('message')}", file=sys.stderr)
        elif long_lived_meta.get("status") == "error":
            print(
                f"warn: long-lived exchange failed: {long_lived_meta.get('message')}",
                file=sys.stderr,
            )

    if health.get("token_type") == "USER" or (
        long_lived_meta.get("status") == "success" and health.get("token_type") != "PAGE"
    ):
        print("info: USER token detected — exchanging for Page token", file=sys.stderr)
        exchange = _root / "deployment" / "exchange-fb-page-token.py"
        proc = subprocess.run(
            [sys.executable, str(exchange)],
            cwd=str(_root),
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            print(proc.stdout or proc.stderr, file=sys.stderr)
            return proc.returncode
        if proc.stdout.strip():
            print(proc.stdout.strip())
        health = check_token_health()

    days_left = health.get("days_left")
    expires_at = health.get("expires_at")
    long_lived_hint = "ok"
    if health.get("token_type") == "PAGE" and expires_at in (0, None) and days_left is None:
        long_lived_hint = "page_token_no_expiry"
    elif isinstance(days_left, int) and days_left < 30:
        long_lived_hint = "short_lived_warning"
        print(
            f"warn: Page token expires in {days_left} days — not never-expiring; "
            "ensure FB_APP_ID/FB_APP_SECRET were used for long-lived exchange",
            file=sys.stderr,
        )

    out = {
        "status": "ok" if health.get("ok") else "error",
        "token_type": health.get("token_type"),
        "ok": health.get("ok"),
        "message_pl": health.get("message_pl"),
        "days_left": days_left,
        "expires_at": expires_at,
        "long_lived_hint": long_lived_hint,
        "long_lived_exchange": long_lived_meta.get("status"),
    }
    print(json.dumps(out, ensure_ascii=False))
    return 0 if health.get("ok") and health.get("token_type") == "PAGE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
