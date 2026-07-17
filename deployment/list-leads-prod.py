#!/usr/bin/env python3
"""List leads (no secrets) for cleanup matching."""
import json
import sqlite3
import sys
from pathlib import Path

db = Path(sys.argv[1] if len(sys.argv) > 1 else "data/jadzia.db")
conn = sqlite3.connect(str(db))
conn.row_factory = sqlite3.Row
rows = conn.execute(
    "SELECT id, email, name, source, game_score, created_at FROM leads ORDER BY id DESC LIMIT 50"
).fetchall()
print(json.dumps([dict(r) for r in rows], ensure_ascii=False, indent=2))
