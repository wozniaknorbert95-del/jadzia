"""
SQLite database layer for Jadzia V4 state management.
Phase 1: Create DB operations (no integration yet).
"""

import sqlite3
import json
import os
from datetime import datetime
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

    # Sessions table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            chat_id TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT 'http',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            active_task_id TEXT,
            task_queue TEXT NOT NULL DEFAULT '[]',
            PRIMARY KEY (chat_id, source)
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
        print(f"[DB MIGRATION] Failed to ensure test_mode column on tasks: {e}")
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

    conn.commit()


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


# ============================================================================
# SESSION OPERATIONS
# ============================================================================

def db_create_or_update_session(chat_id: str, source: str = "http") -> None:
    """
    Create or update session record.

    Args:
        chat_id: Chat identifier
        source: Source type (http/telegram)
    """
    now = datetime.now().isoformat()

    with db_transaction() as conn:
        conn.execute("""
            INSERT INTO sessions (chat_id, source, created_at, updated_at, task_queue)
            VALUES (?, ?, ?, ?, '[]')
            ON CONFLICT(chat_id, source) DO UPDATE SET updated_at = ?
        """, (chat_id, source, now, now, now))


def db_get_session(chat_id: str, source: str = "http") -> Optional[Dict]:
    """
    Get session data.

    Returns:
        Dict with session fields or None if not found
    """
    conn = get_connection()
    row = conn.execute("""
        SELECT * FROM sessions WHERE chat_id = ? AND source = ?
    """, (chat_id, source)).fetchone()

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


def db_set_active_task(chat_id: str, source: str, task_id: Optional[str]) -> None:
    """Set active task for session."""
    with db_transaction() as conn:
        conn.execute("""
            UPDATE sessions
            SET active_task_id = ?, updated_at = ?
            WHERE chat_id = ? AND source = ?
        """, (task_id, datetime.now().isoformat(), chat_id, source))


def db_update_task_queue(chat_id: str, source: str, task_queue: List[str]) -> None:
    """Update task queue for session."""
    with db_transaction() as conn:
        conn.execute("""
            UPDATE sessions
            SET task_queue = ?, updated_at = ?
            WHERE chat_id = ? AND source = ?
        """, (json.dumps(task_queue), datetime.now().isoformat(), chat_id, source))


# ============================================================================
# TASK OPERATIONS
# ============================================================================

def db_create_task(task_data: Dict) -> None:
    """
    Create new task record.

    Args:
        task_data: Dict with task fields (task_id, chat_id, source, operation_id, status, etc.)
    """
    now = datetime.now().isoformat()

    with db_transaction() as conn:
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


def db_update_task(task_id: str, updates: Dict) -> None:
    """
    Update task fields.

    Args:
        task_id: Task identifier
        updates: Dict of fields to update
    """
    now = datetime.now().isoformat()

    # Build SET clause dynamically
    set_parts = ["updated_at = ?"]
    values = [now]

    for key, value in updates.items():
        if key in ["plan", "diffs", "new_contents", "written_files", "errors",
                   "pending_plan", "validation_errors", "deploy_result",
                   "pending_plan_with_questions", "files_to_modify"]:
            # JSON columns
            set_parts.append(f"{key} = ?")
            values.append(json.dumps(value) if value is not None else None)
        elif key in ["dry_run", "test_mode", "awaiting_response"]:
            # Boolean -> integer
            set_parts.append(f"{key} = ?")
            values.append(1 if value else 0)
        else:
            # Regular columns
            set_parts.append(f"{key} = ?")
            values.append(value)

    values.append(task_id)

    sql = f"UPDATE tasks SET {', '.join(set_parts)} WHERE task_id = ?"

    with db_transaction() as conn:
        conn.execute(sql, values)


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
    Used by clear_state() when USE_SQLITE_STATE.
    """
    with db_transaction() as conn:
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
    List all sessions.

    Returns:
        List of (chat_id, source) tuples
    """
    conn = get_connection()
    rows = conn.execute("SELECT chat_id, source FROM sessions").fetchall()
    return [(row["chat_id"], row["source"]) for row in rows]


def db_get_worker_health_session_counts() -> tuple:
    """
    Return (active_sessions, total_tasks, active_tasks, queued_tasks) for worker health.
    Matches the semantics of the JSON scan: sessions with tasks, total task count,
    sessions with active_task_id set, sum of task_queue lengths.
    """
    conn = get_connection()
    rows = conn.execute("""
        SELECT s.active_task_id, s.task_queue,
               (SELECT COUNT(*) FROM tasks t WHERE t.chat_id = s.chat_id AND t.source = s.source) AS task_count
        FROM sessions s
    """).fetchall()
    active_sessions = 0
    total_tasks = 0
    active_tasks = 0
    queued_tasks = 0
    for row in rows:
        task_count = row["task_count"] or 0
        if task_count > 0:
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
