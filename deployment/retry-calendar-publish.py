#!/usr/bin/env python3
"""Retry publish for a calendar entry (approved or failed → publish)."""
import json
import os
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))

_env = _root / ".env"
if _env.exists():
    for line in _env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        os.environ.setdefault(key.strip(), val.strip())

from agent.db import db_get_calendar_entry, db_update_calendar_entry
from agent.commander.publish import publish_calendar_entry_system


def main() -> int:
    entry_id = sys.argv[1] if len(sys.argv) > 1 else ""
    if not entry_id:
        print("usage: retry-calendar-publish.py <entry_id>", file=sys.stderr)
        return 1

    row = db_get_calendar_entry(int(entry_id))
    if not row:
        print(json.dumps({"status": "error", "message": "not found"}))
        return 1

    if row.get("status") in ("failed", "draft"):
        db_update_calendar_entry(int(entry_id), {"status": "approved"})

    row = db_get_calendar_entry(int(entry_id)) or row
    result = publish_calendar_entry_system(
        str(entry_id),
        expected_version=row.get("version"),
        reason="manual_retry_after_token_rotation",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
