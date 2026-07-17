#!/usr/bin/env python3
"""Upsert FB_APP_ID / FB_APP_SECRET into .env without printing values."""
from __future__ import annotations

import re
import sys
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"


def upsert(text: str, key: str, value: str) -> str:
    line = f"{key}={value}"
    if re.search(rf"^{re.escape(key)}=", text, re.MULTILINE):
        return re.sub(rf"^{re.escape(key)}=.*$", line, text, count=1, flags=re.MULTILINE)
    if text and not text.endswith("\n"):
        text += "\n"
    return text + line + "\n"


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: upsert-fb-app-credentials.py <app_id> <app_secret>", file=sys.stderr)
        return 1
    app_id, app_secret = sys.argv[1].strip(), sys.argv[2].strip()
    if not app_id or not app_secret:
        print("error: empty credentials", file=sys.stderr)
        return 1
    if not env_path.exists():
        print(f"error: missing {env_path}", file=sys.stderr)
        return 1
    text = env_path.read_text(encoding="utf-8")
    text = upsert(text, "FB_APP_ID", app_id)
    text = upsert(text, "FB_APP_SECRET", app_secret)
    env_path.write_text(text, encoding="utf-8")
    print('{"status":"ok","FB_APP_ID":"SET","FB_APP_SECRET":"SET"}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
