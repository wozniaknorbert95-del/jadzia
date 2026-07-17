#!/usr/bin/env python3
"""Inspect commander settings keys (no secrets)."""
import sqlite3
from pathlib import Path

db = Path(__file__).resolve().parent.parent / "data" / "jadzia.db"
conn = sqlite3.connect(str(db))
conn.row_factory = sqlite3.Row
for r in conn.execute("SELECT key, value FROM commander_settings ORDER BY key"):
    val = (r["value"] or "")[:200]
    print(f"{r['key']}={val}")
