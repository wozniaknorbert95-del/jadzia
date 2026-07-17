#!/usr/bin/env python3
"""Write SMTP_* keys into /opt/jadzia/.env without printing secrets.

Usage (on VPS):
  venv/bin/python deployment/set-smtp-env.py \\
    --host smtp.gmail.com --port 587 \\
    --user USER@gmail.com --password 'APP_PASSWORD' \\
    --from USER@gmail.com
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"

KEYS = ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "SMTP_FROM")


def _upsert(text: str, key: str, value: str) -> str:
    line = f"{key}={value}"
    pattern = re.compile(rf"^{re.escape(key)}=.*$", re.MULTILINE)
    if pattern.search(text):
        return pattern.sub(line, text, count=1)
    if text and not text.endswith("\n"):
        text += "\n"
    return text + line + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description="Set SMTP_* in .env (no secret stdout)")
    p.add_argument("--host", required=True)
    p.add_argument("--port", default="587")
    p.add_argument("--user", required=True)
    p.add_argument("--password", required=True)
    p.add_argument("--from", dest="from_addr", default="")
    p.add_argument("--env-path", type=Path, default=ENV_PATH)
    args = p.parse_args()

    env_path: Path = args.env_path
    if not env_path.exists():
        print(f"error: missing {env_path}", file=sys.stderr)
        return 1

    from_addr = (args.from_addr or args.user).strip()
    values = {
        "SMTP_HOST": args.host.strip(),
        "SMTP_PORT": str(args.port).strip(),
        "SMTP_USER": args.user.strip(),
        "SMTP_PASSWORD": args.password.strip().replace(" ", ""),
        "SMTP_FROM": from_addr,
    }
    if not values["SMTP_PASSWORD"]:
        print("error: empty password", file=sys.stderr)
        return 1

    text = env_path.read_text(encoding="utf-8")
    for key in KEYS:
        text = _upsert(text, key, values[key])
    env_path.write_text(text, encoding="utf-8")

    # Confirm presence only — never print password
    print("SMTP_ENV=UPDATED")
    print(f"SMTP_HOST={values['SMTP_HOST']}")
    print(f"SMTP_PORT={values['SMTP_PORT']}")
    print(f"SMTP_USER={values['SMTP_USER']}")
    print(f"SMTP_FROM={values['SMTP_FROM']}")
    print("SMTP_PASSWORD=***set***")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
