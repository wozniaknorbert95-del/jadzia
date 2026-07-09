#!/usr/bin/env python3
"""Update FB_ACCESS_TOKEN in .env; auto-exchange USER → PAGE token when needed."""
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


def main() -> int:
    token = (sys.argv[1] if len(sys.argv) > 1 else "").strip()
    if not token:
        print("usage: set-fb-access-token.py <access_token>", file=sys.stderr)
        return 1

    if not env_path.exists():
        print(f"error: missing {env_path}", file=sys.stderr)
        return 1

    text = env_path.read_text(encoding="utf-8")
    line = f"FB_ACCESS_TOKEN={token}"
    if re.search(r"^FB_ACCESS_TOKEN=", text, re.MULTILINE):
        text = re.sub(r"^FB_ACCESS_TOKEN=.*$", line, text, count=1, flags=re.MULTILINE)
    else:
        if text and not text.endswith("\n"):
            text += "\n"
        text += line + "\n"
    env_path.write_text(text, encoding="utf-8")
    _load_env_into_os()

    sys.path.insert(0, str(_root))
    from agent.publishers.facebook import check_token_health

    health = check_token_health()
    if health.get("token_type") == "USER":
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
        print(proc.stdout.strip())
        health = check_token_health()

    print(json.dumps({
        "status": "ok",
        "token_type": health.get("token_type"),
        "ok": health.get("ok"),
        "message_pl": health.get("message_pl"),
        "days_left": health.get("days_left"),
    }, ensure_ascii=False))
    return 0 if health.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
