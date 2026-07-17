#!/usr/bin/env python3
"""Smoke: send one escalation email via _send_delegat_email (no secrets printed).

Run on VPS after SMTP_* are in .env and jadzia restarted (or env loaded here).

  cd /opt/jadzia
  venv/bin/python deployment/smoke-smtp-escalation.py
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"


def load_env() -> dict[str, str]:
    out: dict[str, str] = {}
    if not ENV_PATH.exists():
        return out
    for line in ENV_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, val = stripped.partition("=")
        out[key.strip()] = val.strip().strip('"').strip("'")
    return out


def main() -> int:
    env = load_env()
    for key, val in env.items():
        if key.startswith("SMTP_") or key in {"JWT_SECRET"}:
            os.environ.setdefault(key, val)

    host = os.getenv("SMTP_HOST", "").strip()
    user = os.getenv("SMTP_USER", "").strip()
    password = os.getenv("SMTP_PASSWORD", "").strip()
    port = os.getenv("SMTP_PORT", "587").strip() or "587"

    missing = [k for k, v in (("SMTP_HOST", host), ("SMTP_USER", user), ("SMTP_PASSWORD", password)) if not v]
    if missing:
        print("SMTP_SMOKE=FAIL missing=" + ",".join(missing))
        return 1

    sys.path.insert(0, str(ROOT))
    from agent.commander.escalation import _send_delegat_email
    from agent.commander.settings import get_settings

    settings = get_settings()
    to_email = (settings.get("delegat_email") or user).strip()
    if not to_email:
        print("SMTP_SMOKE=FAIL missing=delegat_email")
        return 1

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    subject = "[SMOKE] COI Commander SMTP"
    body = (
        f"Jadzia COI SMTP smoke OK at {ts}.\n"
        f"Host={host} Port={port} From_user={user}\n"
        f"Safe to ignore / delete."
    )

    ok = _send_delegat_email(subject, body, to_email)
    if not ok:
        print("SMTP_SMOKE=FAIL send=false (see logs; no secrets printed)")
        return 1

    # Mask recipient slightly for logs shared in chat
    masked = to_email[0] + "***@" + to_email.split("@", 1)[-1] if "@" in to_email else "***"
    print("SMTP_SMOKE=PASS")
    print(f"SMTP_HOST={host}")
    print(f"SMTP_PORT={port}")
    print(f"SMTP_TO={masked}")
    print(f"SUBJECT={subject}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
