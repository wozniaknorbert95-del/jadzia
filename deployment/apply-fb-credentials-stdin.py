#!/usr/bin/env python3
"""Apply FB app credentials + access token from stdin JSON. Never echoes secrets."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV = ROOT / ".env"


def upsert(text: str, key: str, value: str) -> str:
    line = f"{key}={value}"
    if re.search(rf"^{re.escape(key)}=", text, re.MULTILINE):
        return re.sub(rf"^{re.escape(key)}=.*$", line, text, count=1, flags=re.MULTILINE)
    if text and not text.endswith("\n"):
        text += "\n"
    return text + line + "\n"


def main() -> int:
    raw = sys.stdin.read()
    data = json.loads(raw)
    app_id = (data.get("app_id") or "").strip()
    app_secret = (data.get("app_secret") or "").strip()
    token = (data.get("token") or "").strip()
    if not app_id or not app_secret or not token:
        print(json.dumps({"status": "error", "message": "need app_id, app_secret, token"}))
        return 1
    if not ENV.exists():
        print(json.dumps({"status": "error", "message": "missing .env"}))
        return 1

    text = ENV.read_text(encoding="utf-8")
    text = upsert(text, "FB_APP_ID", app_id)
    text = upsert(text, "FB_APP_SECRET", app_secret)
    ENV.write_text(text, encoding="utf-8")
    print(json.dumps({"step": "app_credentials", "status": "ok"}))

    proc = subprocess.run(
        [sys.executable, str(ROOT / "deployment" / "set-fb-access-token.py"), token],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
    )
    # Print stdout/stderr but strip any EAAM-looking tokens
    for stream_name, content in (("stdout", proc.stdout), ("stderr", proc.stderr)):
        if not content:
            continue
        redacted = re.sub(r"EAA[A-Za-z0-9]+", "EAA<redacted>", content)
        for line in redacted.strip().splitlines():
            print(f"set_token_{stream_name}: {line}")

    print(json.dumps({"step": "set_token", "exit_code": proc.returncode}))
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
