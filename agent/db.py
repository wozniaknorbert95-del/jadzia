"""
SQLite database layer for Jadzia V4 state management.
Phase 1: Create DB operations (no integration yet).
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
import threading

# Database file location
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "jadzia.db")

# Thread-local storage for connection
_local = threading.local()

# Lock for connection initialization
_conn_lock = threading.Lock()


def get_connection() -> sqlite3.Connection:
    """
    Get thread-local SQLite connection.
    Creates connection if it doesn't exist for this thread.

    Returns:
        sqlite3.Connection with row_factory set
    """
    if not hasattr(_local, 'conn') or _local.conn is None:
        with _conn_lock:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

            # Create connection
            _local.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            _local.conn.row_factory = sqlite3.Row  # Access columns by name

            # Enable foreign keys
            _local.conn.execute("PRAGMA foreign_keys = ON")

            # Initialize schema
            _init_schema(_local.conn)

    return _local.conn


def _init_schema(conn: sqlite3.Connection):
    """Initialize database schema if tables don't exist and run safe migrations."""

    # Sessions table: one row per chat_id (source kept for audit; UNIQUE(chat_id, source) for tasks FK).
    # After running scripts/cleanup_db.py on existing DBs, schema matches this.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            chat_id TEXT NOT NULL PRIMARY KEY,
            source TEXT NOT NULL DEFAULT 'http',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            active_task_id TEXT,
            task_queue TEXT NOT NULL DEFAULT '[]',
            UNIQUE(chat_id, source)
        )
    """)

    # Tasks table (base schema; migrations may extend it)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            chat_id TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT 'http',
            operation_id TEXT NOT NULL,
            status TEXT NOT NULL,
            user_input TEXT,
            dry_run INTEGER NOT NULL DEFAULT 0,
            test_mode INTEGER NOT NULL DEFAULT 0,
            webhook_url TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            completed_at TEXT,
            plan TEXT,
            diffs TEXT,
            new_contents TEXT,
            written_files TEXT,
            errors TEXT,
            pending_plan TEXT,
            validation_errors TEXT,
            retry_count INTEGER NOT NULL DEFAULT 0,
            deploy_result TEXT,
            awaiting_response INTEGER NOT NULL DEFAULT 0,
            awaiting_type TEXT,
            pending_plan_with_questions TEXT,
            last_response TEXT,
            files_to_modify TEXT,
            FOREIGN KEY (chat_id, source) REFERENCES sessions(chat_id, source)
        )
    """)

    # SAFE MIGRATION: ensure test_mode column exists on existing databases.
    try:
        cursor = conn.execute("PRAGMA table_info(tasks)")
        columns = [row[1] for row in cursor.fetchall()]
        if "test_mode" not in columns:
            conn.execute(
                "ALTER TABLE tasks ADD COLUMN test_mode INTEGER NOT NULL DEFAULT 0"
            )
    except Exception as e:
        # Surface a clear error; caller will decide how to handle it.
        import logging
        logging.getLogger(__name__).error("[DB] Migration failed to ensure test_mode column: %s", e)
        raise

    # Indexes
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_chat_source
        ON tasks(chat_id, source)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_task_id
        ON tasks(task_id)
    """)

    # Portal qualification leads (INT-012)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS portal_qual_leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            industry TEXT,
            goal TEXT,
            vehicle TEXT,
            budget_tier TEXT,
            recommended_preset_id TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT 'portal_qual',
            consent INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            expires_at TEXT
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_portal_qual_session
        ON portal_qual_leads(session_id)
    """)

    # WooCommerce orders mirror (INT-002)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL,
            items_json TEXT NOT NULL,
            customer_email TEXT,
            customer_name TEXT,
            total_gross REAL NOT NULL,
            payment_id TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_orders_status
        ON orders(status)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_orders_created_at
        ON orders(created_at)
    """)

    # Game / web leads (INT-004)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            name TEXT,
            source TEXT NOT NULL DEFAULT 'game',
            consent_status INTEGER NOT NULL DEFAULT 0,
            game_score INTEGER,
            reward_tier TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_leads_source
        ON leads(source)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_leads_created_at
        ON leads(created_at)
    """)

    # Social content calendar (INT-010)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS content_calendar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            title TEXT NOT NULL,
            body_nl TEXT NOT NULL,
            scheduled_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'draft',
            source_order_id TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_content_calendar_scheduled
        ON content_calendar(scheduled_at)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_content_calendar_status
        ON content_calendar(status)
    """)

    _migrate_content_calendar_columns(conn)

    conn.commit()


def _migrate_content_calendar_columns(conn: sqlite3.Connection) -> None:
    """Add INT-011 publish columns (idempotent)."""
    new_columns = (
        ("publish_result", "TEXT"),
        ("media_url", "TEXT"),
        ("fb_post_id", "TEXT"),
        ("scheduled_publish_at", "TEXT"),
    )
    for column_name, column_type in new_columns:
        try:
            conn.execute(
                f"ALTER TABLE content_calendar ADD COLUMN {column_name} {column_type}"
            )
        except sqlite3.OperationalError:
            pass


@contextmanager
def db_transaction():
    """
    Context manager for database transactions.

    Usage:
        with db_transaction() as conn:
            conn.execute(...)
            conn.execute(...)
        # Auto-commits on success, rolls back on exception
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def db_transaction_with_retry(max_retries: int = 3, retry_delay: float = 0.1):
    """
    Execute a callable within a transaction, retrying on 'database is locked'.
    Returns a context manager-like wrapper. Usage:

        def do_work(conn):
            conn.execute(...)
        db_execute_with_retry(do_work)

    Or use db_transaction_with_retry() as a decorator for retry logic around
    db_transaction() calls in _sync_to_sqlite.
    """
    import time as _time

    def decorator(fn):
        """fn(conn) will be called inside a transaction with retry."""
        last_err = None
        for attempt in range(max_retries):
            try:
                with db_transaction() as conn:
                    return fn(conn)
            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower() and attempt < max_retries - 1:
                    delay = retry_delay * (2 ** attempt)
                    import logging
                    logging.getLogger(__name__).warning("[DB] database locked, retry %d/%d after %.2fs", attempt + 1, max_retries, delay)
                    _time.sleep(delay)
                    last_err = e
                    continue
                raise
        if last_err:
            raise last_err
    return decorator


# ============================================================================
# SESSION OPERATIONS (chat_id is unique key; source kept for audit after cleanup_db)
# ============================================================================

def _sessions_pk_is_chat_id_only(conn: sqlite3.Connection) -> bool:
    """True if sessions has PRIMARY KEY (chat_id) only (post-cleanup schema)."""
    try:
        pk_info = conn.execute("PRAGMA table_info(sessions)").fetchall()
        pk_cols = [c[1] for c in pk_info if c[5]]
        return len(pk_cols) == 1 and pk_cols[0] == "chat_id"
    except Exception:
        return False


def _exec_create_or_update_session(conn: sqlite3.Connection, chat_id: str, source: str = "http") -> None:
    """Execute session INSERT/UPDATE on given connection (no commit). For atomic batch use."""
    now = datetime.now(timezone.utc).isoformat()
    if _sessions_pk_is_chat_id_only(conn):
        conn.execute("""
            INSERT INTO sessions (chat_id, source, created_at, updated_at, task_queue)
            VALUES (?, ?, ?, ?, '[]')
            ON CONFLICT(chat_id) DO UPDATE SET updated_at = ?
        """, (chat_id, source, now, now, now))
    else:
        conn.execute("""
            INSERT INTO sessions (chat_id, source, created_at, updated_at, task_queue)
            VALUES (?, ?, ?, ?, '[]')
            ON CONFLICT(chat_id, source) DO UPDATE SET updated_at = ?
        """, (chat_id, source, now, now, now))


def db_create_or_update_session(chat_id: str, source: str = "http") -> None:
    """
    Create or update session record.

    Args:
        chat_id: Chat identifier
        source: Source type (http/telegram)
    """
    with db_transaction() as conn:
        _exec_create_or_update_session(conn, chat_id, source)


def db_get_session(chat_id: str, source: str = "http") -> Optional[Dict]:
    """
    Get session data by chat_id. When schema has one row per chat_id, source is ignored for lookup.
    When schema has (chat_id, source), prefers telegram over http for same chat_id.
    """
    conn = get_connection()
    if _sessions_pk_is_chat_id_only(conn):
        row = conn.execute("SELECT * FROM sessions WHERE chat_id = ?", (chat_id,)).fetchone()
    else:
        row = conn.execute(
            "SELECT * FROM sessions WHERE chat_id = ? AND source = ?", (chat_id, source)
        ).fetchone()
        if not row:
            row = conn.execute(
                "SELECT * FROM sessions WHERE chat_id = ? ORDER BY CASE source WHEN 'telegram' THEN 0 ELSE 1 END LIMIT 1",
                (chat_id,),
            ).fetchone()

    if not row:
        return None

    return {
        "chat_id": row["chat_id"],
        "source": row["source"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "active_task_id": row["active_task_id"],
        "task_queue": json.loads(row["task_queue"])
    }


def _exec_set_active_task(conn: sqlite3.Connection, chat_id: str, source: str, task_id: Optional[str]) -> None:
    """Execute active_task update on given connection (no commit). For atomic batch use."""
    now = datetime.now(timezone.utc).isoformat()
    if _sessions_pk_is_chat_id_only(conn):
        conn.execute(
            "UPDATE sessions SET active_task_id = ?, updated_at = ? WHERE chat_id = ?",
            (task_id, now, chat_id),
        )
    else:
        conn.execute(
            "UPDATE sessions SET active_task_id = ?, updated_at = ? WHERE chat_id = ? AND source = ?",
            (task_id, now, chat_id, source),
        )


def db_set_active_task(chat_id: str, source: str, task_id: Optional[str]) -> None:
    """Set active task for session."""
    with db_transaction() as conn:
        _exec_set_active_task(conn, chat_id, source, task_id)


def _exec_update_task_queue(conn: sqlite3.Connection, chat_id: str, source: str, task_queue: List[str]) -> None:
    """Execute task_queue update on given connection (no commit). For atomic batch use."""
    now = datetime.now(timezone.utc).isoformat()
    if _sessions_pk_is_chat_id_only(conn):
        conn.execute(
            "UPDATE sessions SET task_queue = ?, updated_at = ? WHERE chat_id = ?",
            (json.dumps(task_queue), now, chat_id),
        )
    else:
        conn.execute(
            "UPDATE sessions SET task_queue = ?, updated_at = ? WHERE chat_id = ? AND source = ?",
            (json.dumps(task_queue), now, chat_id, source),
        )


def db_update_task_queue(chat_id: str, source: str, task_queue: List[str]) -> None:
    """Update task queue for session."""
    with db_transaction() as conn:
        _exec_update_task_queue(conn, chat_id, source, task_queue)


# ============================================================================
# TASK OPERATIONS
# ============================================================================

def _exec_create_task(conn: sqlite3.Connection, task_data: Dict) -> None:
    """Execute INSERT for task on given connection (no commit). For atomic batch use."""
    now = datetime.now(timezone.utc).isoformat()
    conn.execute("""
        INSERT INTO tasks (
            task_id, chat_id, source, operation_id, status,
            user_input, dry_run, test_mode, webhook_url,
            created_at, updated_at,
            plan, diffs, new_contents, written_files, errors,
            pending_plan, validation_errors, retry_count,
            deploy_result, awaiting_response, awaiting_type,
            pending_plan_with_questions, last_response, files_to_modify
        ) VALUES (
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?
        )
    """, (
        task_data["task_id"],
        task_data["chat_id"],
        task_data.get("source", "http"),
        task_data["operation_id"],
        task_data["status"],
        task_data.get("user_input"),
        1 if task_data.get("dry_run") else 0,
        1 if task_data.get("test_mode") else 0,
        task_data.get("webhook_url"),
        task_data.get("created_at", now),
        now,
        json.dumps(task_data.get("plan")) if task_data.get("plan") else None,
        json.dumps(task_data.get("diffs")) if task_data.get("diffs") else None,
        json.dumps(task_data.get("new_contents")) if task_data.get("new_contents") else None,
        json.dumps(task_data.get("written_files")) if task_data.get("written_files") else None,
        json.dumps(task_data.get("errors", [])),
        json.dumps(task_data.get("pending_plan")) if task_data.get("pending_plan") else None,
        json.dumps(task_data.get("validation_errors")) if task_data.get("validation_errors") else None,
        task_data.get("retry_count", 0),
        json.dumps(task_data.get("deploy_result")) if task_data.get("deploy_result") else None,
        1 if task_data.get("awaiting_response") else 0,
        task_data.get("awaiting_type"),
        json.dumps(task_data.get("pending_plan_with_questions")) if task_data.get("pending_plan_with_questions") else None,
        task_data.get("last_response"),
        json.dumps(task_data.get("files_to_modify")) if task_data.get("files_to_modify") else None
    ))


def _exec_update_task(conn: sqlite3.Connection, task_id: str, updates: Dict) -> None:
    """Execute UPDATE for task on given connection (no commit). For atomic batch use."""
    now = datetime.now(timezone.utc).isoformat()
    set_parts = ["updated_at = ?"]
    values = [now]
    for key, value in updates.items():
        if key in ["plan", "diffs", "new_contents", "written_files", "errors",
                   "pending_plan", "validation_errors", "deploy_result",
                   "pending_plan_with_questions", "files_to_modify"]:
            set_parts.append(f"{key} = ?")
            values.append(json.dumps(value) if value is not None else None)
        elif key in ["dry_run", "test_mode", "awaiting_response"]:
            set_parts.append(f"{key} = ?")
            values.append(1 if value else 0)
        else:
            set_parts.append(f"{key} = ?")
            values.append(value)
    values.append(task_id)
    sql = f"UPDATE tasks SET {', '.join(set_parts)} WHERE task_id = ?"
    conn.execute(sql, values)


def db_create_task(task_data: Dict) -> None:
    """
    Create new task record.

    Args:
        task_data: Dict with task fields (task_id, chat_id, source, operation_id, status, etc.)
    """
    with db_transaction() as conn:
        _exec_create_task(conn, task_data)


def db_update_task(task_id: str, updates: Dict) -> None:
    """
    Update task fields.

    Args:
        task_id: Task identifier
        updates: Dict of fields to update
    """
    with db_transaction() as conn:
        _exec_update_task(conn, task_id, updates)


def db_get_task(task_id: str) -> Optional[Dict]:
    """
    Get task by ID.

    Returns:
        Dict with task fields or None if not found
    """
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()

    if not row:
        return None

    return _row_to_task_dict(row)


def db_get_tasks_for_session(chat_id: str, source: str = "http") -> List[Dict]:
    """Get all tasks for a session."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM tasks
        WHERE chat_id = ? AND source = ?
        ORDER BY created_at
    """, (chat_id, source)).fetchall()

    return [_row_to_task_dict(row) for row in rows]


def db_get_active_task(chat_id: str, source: str = "http") -> Optional[str]:
    """Return active_task_id for session from sessions table. Single source of truth."""
    conn = get_connection()
    row = conn.execute(
        "SELECT active_task_id FROM sessions WHERE chat_id = ?",
        (chat_id,),
    ).fetchone()
    return row["active_task_id"] if row and row["active_task_id"] else None


def db_get_awaiting_approval_task(chat_id: str, source: str = "http") -> Optional[Dict]:
    """
    Return the single task for this session that is awaiting approval
    (status='diff_ready' and awaiting_response=1). Used as fallback for Telegram "TAK" flow.
    """
    conn = get_connection()
    row = conn.execute("""
        SELECT * FROM tasks
        WHERE chat_id = ? AND source = ? AND status = 'diff_ready' AND awaiting_response = 1
        ORDER BY updated_at DESC LIMIT 1
    """, (chat_id, source)).fetchone()

    if not row:
        return None

    return _row_to_task_dict(row)


def db_get_last_active_task(chat_id: str, source: str = "http") -> Optional[Dict]:
    """
    Return the most recent non-terminal task for this session
    (status NOT IN ('completed','failed','rolled_back')).
    Used as fallback for Telegram approval when plan_approval is not yet diff_ready.
    """
    conn = get_connection()
    row = conn.execute("""
        SELECT * FROM tasks
        WHERE chat_id = ? AND source = ?
        AND status NOT IN ('completed', 'failed', 'rolled_back')
        ORDER BY updated_at DESC LIMIT 1
    """, (chat_id, source)).fetchone()

    if not row:
        return None

    return _row_to_task_dict(row)


def db_find_session_by_task_id(task_id: str) -> Optional[tuple]:
    """
    Find (chat_id, source) for a given task_id.

    Returns:
        (chat_id, source) tuple or None
    """
    conn = get_connection()
    row = conn.execute("""
        SELECT chat_id, source FROM tasks WHERE task_id = ?
    """, (task_id,)).fetchone()

    if not row:
        return None

    return (row["chat_id"], row["source"])


def _row_to_task_dict(row: sqlite3.Row) -> Dict:
    """Convert SQLite row to task dictionary."""
    task = dict(row)

    # Parse JSON columns
    json_columns = [
        "plan", "diffs", "new_contents", "written_files", "errors",
        "pending_plan", "validation_errors", "deploy_result",
        "pending_plan_with_questions", "files_to_modify"
    ]

    for col in json_columns:
        if task.get(col):
            try:
                task[col] = json.loads(task[col])
            except Exception:
                task[col] = None

    # Convert integers to booleans
    task["dry_run"] = bool(task.get("dry_run"))
    task["test_mode"] = bool(task.get("test_mode"))
    task["awaiting_response"] = bool(task.get("awaiting_response"))

    return task


# ============================================================================
# DELETE / CLEANUP
# ============================================================================

def db_delete_session(chat_id: str, source: str = "http") -> None:
    """
    Delete a session and all its tasks.
    Used by clear_state(). With chat_id-only schema, deletes by chat_id.
    """
    with db_transaction() as conn:
        if _sessions_pk_is_chat_id_only(conn):
            conn.execute("DELETE FROM tasks WHERE chat_id = ?", (chat_id,))
            conn.execute("DELETE FROM sessions WHERE chat_id = ?", (chat_id,))
        else:
            conn.execute("DELETE FROM tasks WHERE chat_id = ? AND source = ?", (chat_id, source))
            conn.execute("DELETE FROM sessions WHERE chat_id = ? AND source = ?", (chat_id, source))


def db_list_sessions_updated_before(cutoff_iso: str) -> List[tuple]:
    """
    List (chat_id, source) for sessions with updated_at < cutoff.
    Used by cleanup_old_sessions() for SQLite.
    """
    conn = get_connection()
    rows = conn.execute("""
        SELECT chat_id, source FROM sessions
        WHERE updated_at < ?
    """, (cutoff_iso,)).fetchall()
    return [(row["chat_id"], row["source"]) for row in rows]


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def db_list_all_sessions() -> List[tuple]:
    """
    List all sessions. One entry per chat_id (after cleanup_db, source is canonical).

    Returns:
        List of (chat_id, source) tuples
    """
    conn = get_connection()
    rows = conn.execute("SELECT chat_id, source FROM sessions").fetchall()
    if _sessions_pk_is_chat_id_only(conn):
        return [(row["chat_id"], row["source"]) for row in rows]
    # Old schema: dedupe by chat_id (prefer telegram)
    seen: set = set()
    out = []
    for row in sorted(rows, key=lambda r: (r["chat_id"], 0 if r["source"] == "telegram" else 1)):
        if row["chat_id"] not in seen:
            seen.add(row["chat_id"])
            out.append((row["chat_id"], row["source"]))
    return out


def db_get_worker_health_session_counts() -> tuple:
    """
    Return (active_sessions, total_tasks, active_tasks, queued_tasks) for worker health.
    active_sessions: sessions with at least one non-terminal task (planning, in_progress, etc.).
    total_tasks: all tasks. active_tasks: sessions with active_task_id set. queued_tasks: sum of queue lengths.
    """
    conn = get_connection()
    rows = conn.execute("""
        SELECT s.active_task_id, s.task_queue,
               (SELECT COUNT(*) FROM tasks t WHERE t.chat_id = s.chat_id AND t.source = s.source) AS task_count,
               (SELECT COUNT(*) FROM tasks t WHERE t.chat_id = s.chat_id AND t.source = s.source
                AND t.status NOT IN ('completed', 'failed', 'rolled_back')) AS non_terminal_count
        FROM sessions s
    """).fetchall()
    active_sessions = 0
    total_tasks = 0
    active_tasks = 0
    queued_tasks = 0
    for row in rows:
        task_count = row["task_count"] or 0
        non_terminal = row["non_terminal_count"] or 0
        if non_terminal > 0:
            active_sessions += 1
        total_tasks += task_count
        if row["active_task_id"]:
            active_tasks += 1
        try:
            q = json.loads(row["task_queue"] or "[]")
            queued_tasks += len(q) if isinstance(q, list) else 0
        except Exception:
            pass
    return (active_sessions, total_tasks, active_tasks, queued_tasks)


def db_health_check() -> bool:
    """Check if database is accessible."""
    try:
        conn = get_connection()
        conn.execute("SELECT 1").fetchone()
        return True
    except Exception:
        return False


def db_get_dashboard_metrics() -> Dict[str, Any]:
    """
    Return raw dashboard metrics from tasks table (no status mapping; done in API).
    Used by GET /worker/dashboard.
    """
    conn = get_connection()

    total_tasks = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]

    by_status_rows = conn.execute(
        "SELECT status, COUNT(*) AS cnt FROM tasks GROUP BY status"
    ).fetchall()
    by_status_raw = [{"status": row["status"], "count": row["cnt"]} for row in by_status_rows]

    test_mode_tasks = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE test_mode = 1"
    ).fetchone()[0]

    production_tasks = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE test_mode = 0"
    ).fetchone()[0]

    recent_rows = conn.execute(
        """
        SELECT task_id, status, test_mode, dry_run, created_at, updated_at, completed_at
        FROM tasks ORDER BY created_at DESC LIMIT 20
        """
    ).fetchall()
    recent_tasks_raw = [
        {
            "task_id": row["task_id"],
            "status": row["status"],
            "test_mode": row["test_mode"],
            "dry_run": row["dry_run"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "completed_at": row["completed_at"],
        }
        for row in recent_rows
    ]

    cutoff_24h = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    errors_last_24h = conn.execute(
        """
        SELECT COUNT(*) FROM tasks
        WHERE status IN ('failed', 'rolled_back') AND updated_at >= ?
        """,
        (cutoff_24h,),
    ).fetchone()[0]

    cutoff_7d = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    avg_row = conn.execute(
        """
        SELECT AVG(MIN(
            (julianday(COALESCE(completed_at, updated_at)) - julianday(created_at)) * 86400,
            7200
        )) AS avg_sec
        FROM tasks
        WHERE status IN ('completed', 'failed', 'rolled_back')
          AND created_at IS NOT NULL
          AND (completed_at IS NOT NULL OR updated_at IS NOT NULL)
          AND (COALESCE(completed_at, updated_at) >= ?)
        """,
        (cutoff_7d,),
    ).fetchone()
    avg_val = avg_row["avg_sec"] if avg_row and avg_row["avg_sec"] is not None else None
    avg_duration_seconds = round(avg_val, 1) if avg_val is not None else None

    return {
        "total_tasks": total_tasks,
        "by_status_raw": by_status_raw,
        "test_mode_tasks": test_mode_tasks,
        "production_tasks": production_tasks,
        "recent_tasks_raw": recent_tasks_raw,
        "errors_last_24h": errors_last_24h,
        "avg_duration_seconds": avg_duration_seconds,
    }


def db_mark_tasks_failed(task_ids: List[str], reason: str) -> Dict[str, Any]:
    """
    Mark selected tasks as failed (without deleting them).

    Returns dict with:
        {
            "updated": [task_ids_marked_failed],
            "skipped_terminal": [task_ids_already_completed_or_failed],
            "not_found": [task_ids_not_in_db],
        }
    """
    updated: List[str] = []
    skipped_terminal: List[str] = []
    not_found: List[str] = []

    for task_id in task_ids:
        task = db_get_task(task_id)
        if not task:
            not_found.append(task_id)
            continue

        status = task.get("status")
        if status in ("completed", "failed", "rolled_back"):
            skipped_terminal.append(task_id)
            continue

        errors = task.get("errors") or []
        if not isinstance(errors, list):
            errors = [str(errors)]

        msg = f"Marked as failed by cleanup: {reason} (was {status})"
        errors.append(msg)

        updates: Dict[str, Any] = {
            "status": "failed",
            "errors": errors,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
        db_update_task(task_id, updates)
        updated.append(task_id)

    return {
        "updated": updated,
        "skipped_terminal": skipped_terminal,
        "not_found": not_found,
    }


# ============================================================================
# ORDER OPERATIONS (INT-002)
# ============================================================================

def db_upsert_order(order_data: Dict) -> Optional[str]:
    """
    Insert or update a WooCommerce order mirror row.

    Args:
        order_data: Dict with order_id, status, items (list), customer (dict),
                    total_gross, payment_id (optional).

    Returns:
        order_internal_id as string on success, None on failure.
    """
    order_id = order_data.get("order_id")
    if not order_id:
        return None

    now = datetime.now(timezone.utc).isoformat()
    items = order_data.get("items") or []
    customer = order_data.get("customer") or {}

    try:
        with db_transaction() as conn:
            existing = conn.execute(
                "SELECT id, created_at FROM orders WHERE order_id = ?",
                (order_id,),
            ).fetchone()

            if existing:
                conn.execute(
                    """
                    UPDATE orders SET
                        status = ?,
                        items_json = ?,
                        customer_email = ?,
                        customer_name = ?,
                        total_gross = ?,
                        payment_id = ?,
                        updated_at = ?
                    WHERE order_id = ?
                    """,
                    (
                        order_data["status"],
                        json.dumps(items),
                        customer.get("email"),
                        customer.get("name"),
                        order_data["total_gross"],
                        order_data.get("payment_id"),
                        now,
                        order_id,
                    ),
                )
                internal_id = str(existing["id"])
            else:
                cursor = conn.execute(
                    """
                    INSERT INTO orders (
                        order_id, status, items_json,
                        customer_email, customer_name,
                        total_gross, payment_id,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        order_id,
                        order_data["status"],
                        json.dumps(items),
                        customer.get("email"),
                        customer.get("name"),
                        order_data["total_gross"],
                        order_data.get("payment_id"),
                        now,
                        now,
                    ),
                )
                internal_id = str(cursor.lastrowid)

        return internal_id
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(
            "[DB] db_upsert_order failed order_id=%s: %s", order_id, e
        )
        return None


def db_get_order_by_wc_id(order_id: str) -> Optional[Dict]:
    """Get order by WooCommerce order_id."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM orders WHERE order_id = ?", (order_id,)
    ).fetchone()
    if not row:
        return None
    return _row_to_order_dict(row)


def db_get_order_by_internal_id(internal_id: int) -> Optional[Dict]:
    """Get order by internal autoincrement id."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM orders WHERE id = ?", (internal_id,)
    ).fetchone()
    if not row:
        return None
    return _row_to_order_dict(row)


def _row_to_order_dict(row: sqlite3.Row) -> Dict:
    """Convert orders row to dict with parsed items."""
    order = dict(row)
    order["order_internal_id"] = str(order.pop("id"))
    if order.get("items_json"):
        try:
            order["items"] = json.loads(order["items_json"])
        except Exception:
            order["items"] = []
    else:
        order["items"] = []
    order.pop("items_json", None)
    order["customer"] = {
        "email": order.pop("customer_email", None),
        "name": order.pop("customer_name", None),
    }
    return order


# ============================================================================
# LEAD OPERATIONS (INT-004)
# ============================================================================

def db_create_lead(lead_data: Dict) -> tuple[Optional[str], str]:
    """
    Insert a lead if email is unique.

    Returns:
        (lead_id, sync_status) where sync_status is success|duplicate|fail
    """
    email = (lead_data.get("email") or "").strip().lower()
    if not email:
        return None, "fail"

    if not lead_data.get("consent_status"):
        return None, "fail"

    now = datetime.now(timezone.utc).isoformat()

    try:
        with db_transaction() as conn:
            existing = conn.execute(
                "SELECT id FROM leads WHERE email = ?", (email,)
            ).fetchone()
            if existing:
                return str(existing["id"]), "duplicate"

            cursor = conn.execute(
                """
                INSERT INTO leads (
                    email, name, source, consent_status,
                    game_score, reward_tier, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    email,
                    lead_data.get("name"),
                    lead_data.get("source", "game"),
                    1,
                    lead_data.get("game_score"),
                    lead_data.get("reward_tier"),
                    now,
                    now,
                ),
            )
            return str(cursor.lastrowid), "success"
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(
            "[DB] db_create_lead failed email=%s: %s", email[:3] + "***", e
        )
        return None, "fail"


def db_get_lead_by_email(email: str) -> Optional[Dict]:
    """Get lead by email (normalized lowercase)."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM leads WHERE email = ?", (email.strip().lower(),)
    ).fetchone()
    if not row:
        return None
    return _row_to_lead_dict(row)


def db_get_lead_by_id(lead_id: int) -> Optional[Dict]:
    """Get lead by internal id."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM leads WHERE id = ?", (lead_id,)
    ).fetchone()
    if not row:
        return None
    return _row_to_lead_dict(row)


def _row_to_lead_dict(row: sqlite3.Row) -> Dict:
    """Convert leads row to dict."""
    lead = dict(row)
    lead["lead_id"] = str(lead.pop("id"))
    lead["consent_status"] = bool(lead.get("consent_status"))
    return lead


# ============================================================================
# Content calendar operations (INT-010)
# ============================================================================

_VALID_CALENDAR_STATUSES = frozenset(
    {"draft", "pending_approval", "approved", "published", "cancelled", "failed"}
)
_VALID_PLATFORMS = frozenset({"facebook", "tiktok"})


def db_create_calendar_entry(entry_data: Dict) -> tuple[str, str]:
    """
    Insert content calendar entry.

    Returns:
        (entry_id, sync_status) where sync_status is success|fail
    """
    platform = entry_data.get("platform", "")
    if platform not in _VALID_PLATFORMS:
        return "", "fail"

    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO content_calendar (
                platform, title, body_nl, scheduled_at, status,
                source_order_id, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                platform,
                entry_data["title"],
                entry_data["body_nl"],
                entry_data["scheduled_at"],
                entry_data.get("status", "draft"),
                entry_data.get("source_order_id"),
                now,
                now,
            ),
        )
        conn.commit()
        return str(cursor.lastrowid), "success"
    except Exception:
        conn.rollback()
        return "", "fail"


def db_list_calendar_entries(
    status: Optional[str] = None,
    platform: Optional[str] = None,
    limit: int = 50,
) -> List[Dict]:
    """List calendar entries with optional filters."""
    conn = get_connection()
    query = "SELECT * FROM content_calendar WHERE 1=1"
    params: List[Any] = []

    if status:
        query += " AND status = ?"
        params.append(status)
    if platform:
        query += " AND platform = ?"
        params.append(platform)

    query += " ORDER BY scheduled_at ASC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    return [_row_to_calendar_dict(row) for row in rows]


def db_get_calendar_entry(entry_id: int) -> Optional[Dict]:
    """Get calendar entry by internal id."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM content_calendar WHERE id = ?", (entry_id,)
    ).fetchone()
    if not row:
        return None
    return _row_to_calendar_dict(row)


def db_update_calendar_entry(entry_id: int, updates: Dict) -> bool:
    """Update calendar entry fields. Returns True on success."""
    allowed = {
        "title",
        "body_nl",
        "scheduled_at",
        "status",
        "publish_result",
        "media_url",
        "fb_post_id",
        "scheduled_publish_at",
    }
    filtered = {k: v for k, v in updates.items() if k in allowed and v is not None}
    if not filtered:
        return False
    if "status" in filtered and filtered["status"] not in _VALID_CALENDAR_STATUSES:
        return False

    filtered["updated_at"] = datetime.now(timezone.utc).isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in filtered)
    values = list(filtered.values()) + [entry_id]

    conn = get_connection()
    try:
        cursor = conn.execute(
            f"UPDATE content_calendar SET {set_clause} WHERE id = ?",
            values,
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        conn.rollback()
        return False


def db_get_completed_orders_for_calendar(limit: int = 10) -> List[Dict]:
    """Recent completed/processing orders for case-study suggestions."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT order_id, status, total_gross, customer_name, created_at
        FROM orders
        WHERE status IN ('completed', 'processing')
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [dict(row) for row in rows]


def _row_to_calendar_dict(row: sqlite3.Row) -> Dict:
    """Convert content_calendar row to API dict."""
    entry = dict(row)
    entry["entry_id"] = str(entry.pop("id"))
    return entry


# ============================================================================
# Manual testing
# ============================================================================

if __name__ == "__main__":
    import uuid
    # Test basic operations (use unique task_id so run is idempotent)
    test_task_id = "test_task_" + str(uuid.uuid4())[:8]
    print("Testing DB layer...")

    # Create session
    db_create_or_update_session("test_chat", "http")
    print("[OK] Session created")

    # Create task
    task_data = {
        "task_id": test_task_id,
        "chat_id": "test_chat",
        "source": "http",
        "operation_id": "op_001",
        "status": "planning",
        "user_input": "test input",
        "dry_run": False
    }
    db_create_task(task_data)
    print("[OK] Task created")

    # Read task back
    task = db_get_task(test_task_id)
    print(f"[OK] Task retrieved: {task['task_id']}")

    # Update task
    db_update_task(test_task_id, {"status": "completed"})
    print("[OK] Task updated")

    # Find session by task
    result = db_find_session_by_task_id(test_task_id)
    print(f"[OK] Found session: {result}")

    # Health check
    healthy = db_health_check()
    print(f"[OK] Health check: {healthy}")

    print("\nAll tests passed! DB layer working.")
