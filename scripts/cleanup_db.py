"""
Consolidate sessions by chat_id: merge duplicate (http + telegram) rows into one,
then enforce UNIQUE(chat_id) by recreating the sessions table.

Run once after deploying the session-consolidation change.
Usage: python scripts/cleanup_db.py [--dry-run] [--verbose] [--remove-test-sessions]

Before running: back up the database (e.g. cp data/jadzia.db data/jadzia.db.bak).
"""

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def get_db_path() -> str:
    return os.getenv("JADZIA_DB_PATH") or os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "data", "jadzia.db")
    )


def get_connection(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = OFF")  # allow recreate during migration
    return conn


def has_composite_pk_sessions(conn: sqlite3.Connection) -> bool:
    """True if sessions table has (chat_id, source) composite PK (old schema)."""
    try:
        info = conn.execute("PRAGMA table_info(sessions)").fetchall()
        if not info:
            return False
        pk = conn.execute("PRAGMA index_list(sessions)").fetchall()
        # SQLite: for table without explicit PK, no sqlite_sequence; with PK(chat_id, source) we have one index.
        # Simpler: check if we have more than one row for any chat_id (duplicates exist).
        rows = conn.execute("SELECT chat_id, COUNT(*) AS c FROM sessions GROUP BY chat_id HAVING c > 1").fetchall()
        return len(rows) > 0
    except Exception:
        return False


def run_cleanup(db_path: str, dry_run: bool, verbose: bool, remove_test_sessions: bool) -> None:
    conn = get_connection(db_path)

    try:
        # 1) Merge duplicate sessions (same chat_id, different source)
        rows = conn.execute(
            "SELECT chat_id FROM sessions GROUP BY chat_id HAVING COUNT(*) > 1"
        ).fetchall()
        duplicate_chat_ids = [r[0] for r in rows]

        for chat_id in duplicate_chat_ids:
            session_rows = conn.execute(
                "SELECT chat_id, source, created_at, updated_at, active_task_id, task_queue FROM sessions WHERE chat_id = ?",
                (chat_id,),
            ).fetchall()
            if len(session_rows) < 2:
                continue
            # Prefer telegram over http
            by_source = {r["source"]: dict(r) for r in session_rows}
            if "telegram" in by_source and "http" in by_source:
                tel = by_source["telegram"]
                http = by_source["http"]
                # Merge task_queue: combine and dedupe (prefer order: telegram then http)
                q_tel = json.loads(tel["task_queue"] or "[]")
                q_http = json.loads(http["task_queue"] or "[]")
                seen = set(q_tel)
                for tid in q_http:
                    if tid not in seen:
                        q_tel.append(tid)
                        seen.add(tid)
                merged_queue = json.dumps(q_tel)
                active = tel["active_task_id"] or http["active_task_id"]
                # Point all tasks for this chat_id to telegram
                conn.execute(
                    "UPDATE tasks SET source = ? WHERE chat_id = ? AND source = ?",
                    ("telegram", chat_id, "http"),
                )
                # Update telegram row with merged state
                from datetime import datetime, timezone
                now = datetime.now(timezone.utc).isoformat()
                conn.execute(
                    """UPDATE sessions SET task_queue = ?, active_task_id = ?, updated_at = ?
                       WHERE chat_id = ? AND source = ?""",
                    (merged_queue, active, now, chat_id, "telegram"),
                )
                # Remove http session row
                conn.execute("DELETE FROM sessions WHERE chat_id = ? AND source = ?", (chat_id, "http"))
                if verbose:
                    print(f"  Merged chat_id={chat_id}: telegram kept, http removed; queue merged.")
            else:
                # Two rows but not http+telegram (e.g. two http) — keep one
                first = session_rows[0]
                for r in session_rows[1:]:
                    conn.execute(
                        "DELETE FROM sessions WHERE chat_id = ? AND source = ?",
                        (chat_id, r["source"]),
                    )
                if verbose:
                    print(f"  Deduplicated chat_id={chat_id}: kept one row.")

        # 2) Optional: remove test-looking sessions (phase4_*, sprint*, test_*)
        if remove_test_sessions:
            patterns = ("phase4_%", "sprint%", "test_%")
            for pattern in patterns:
                cur = conn.execute(
                    "SELECT chat_id, source FROM sessions WHERE chat_id LIKE ?", (pattern,)
                )
                to_remove = cur.fetchall()
                for row in to_remove:
                    conn.execute(
                        "DELETE FROM tasks WHERE chat_id = ? AND source = ?",
                        (row["chat_id"], row["source"]),
                    )
                    conn.execute(
                        "DELETE FROM sessions WHERE chat_id = ? AND source = ?",
                        (row["chat_id"], row["source"]),
                    )
                    if verbose:
                        print(f"  Removed test session: {row['chat_id']}/{row['source']}")

        # 3) Recreate sessions table with UNIQUE(chat_id) — PRIMARY KEY (chat_id)
        # Check if already single-column PK (e.g. after previous run)
        pk_info = conn.execute("PRAGMA table_info(sessions)").fetchall()
        pk_cols = [c[1] for c in pk_info if c[5]]  # c[5] is pk index (0 = not in pk)
        if len(pk_cols) == 1 and pk_cols[0] == "chat_id":
            if verbose:
                print("  Sessions already has chat_id as primary key; skip recreate.")
            if not dry_run:
                conn.commit()
            return

        # Create new table (PK chat_id; UNIQUE(chat_id, source) so tasks FK still valid)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions_new (
                chat_id TEXT NOT NULL PRIMARY KEY,
                source TEXT NOT NULL DEFAULT 'http',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                active_task_id TEXT,
                task_queue TEXT NOT NULL DEFAULT '[]',
                UNIQUE(chat_id, source)
            )
        """)
        # Copy one row per chat_id (prefer telegram; INSERT OR REPLACE handles any remaining duplicates)
        conn.execute("""
            INSERT OR REPLACE INTO sessions_new (chat_id, source, created_at, updated_at, active_task_id, task_queue)
            SELECT chat_id, source, created_at, updated_at, active_task_id, task_queue
            FROM sessions
            ORDER BY chat_id, CASE source WHEN 'telegram' THEN 0 ELSE 1 END
        """)
        conn.execute("DROP TABLE sessions")
        conn.execute("ALTER TABLE sessions_new RENAME TO sessions")
        if verbose:
            print("  Recreated sessions table with PRIMARY KEY (chat_id).")

        if not dry_run:
            conn.commit()
            print("Cleanup committed.")
        else:
            conn.rollback()
            print("Dry run: no changes committed.")
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Consolidate sessions by chat_id and enforce UNIQUE(chat_id).")
    parser.add_argument("--dry-run", action="store_true", help="Do not commit changes.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output.")
    parser.add_argument("--remove-test-sessions", action="store_true", help="Remove sessions matching phase4_*, sprint*, test_*.")
    args = parser.parse_args()

    db_path = get_db_path()
    if not os.path.isfile(db_path):
        print(f"Database not found: {db_path}", file=sys.stderr)
        return 1
    print(f"Using database: {db_path}")
    if args.dry_run:
        print("DRY RUN — no changes will be committed.")
    run_cleanup(db_path, dry_run=args.dry_run, verbose=args.verbose, remove_test_sessions=args.remove_test_sessions)
    return 0


if __name__ == "__main__":
    sys.exit(main())
