#!/usr/bin/env python3
"""Inspect content_calendar entries on prod (no secrets)."""
import json
import sqlite3
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
db = _root / "data" / "jadzia.db"
if len(sys.argv) > 1:
    db = Path(sys.argv[1])

conn = sqlite3.connect(str(db))
conn.row_factory = sqlite3.Row
rows = conn.execute(
    """
    SELECT id, title, status, content_type, media_url,
           scheduled_publish_at, fb_post_id, publish_result, updated_at, version
    FROM content_calendar
    ORDER BY id DESC
    LIMIT 10
    """
).fetchall()
for r in rows:
    d = dict(r)
    pr = d.pop("publish_result", None)
    print(json.dumps(d, ensure_ascii=False))
    if pr:
        try:
            parsed = json.loads(pr)
            print("  publish_result:", json.dumps(parsed, ensure_ascii=False)[:800])
        except json.JSONDecodeError:
            print("  publish_result:", pr[:800])
