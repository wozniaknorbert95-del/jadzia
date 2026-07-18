"""Read-only: confirm Commander queue still exposes disposition/approve actions."""
from pathlib import Path

q = Path("/opt/jadzia/agent/commander/queue.py").read_text(encoding="utf-8")
needles = ("available_actions", "approve", "disposition", "CRITICAL")
hits = {n: (n in q) for n in needles}
print("QUEUE_MARKERS", hits)
assert hits["available_actions"] and hits["disposition"], "HITL actions missing"

import sqlite3

c = sqlite3.connect("/opt/jadzia/data/jadzia.db")
open_n = c.execute(
    "SELECT COUNT(*) FROM commander_tickets WHERE status='open'"
).fetchone()[0]
print("OPEN_TICKETS", open_n)
print("HITL_SMOKE_OK")
