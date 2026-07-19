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
            schema_version TEXT NOT NULL DEFAULT 'int-002.v1',
            currency TEXT,
            total_net REAL,
            tax_total REAL,
            payment_status TEXT,
            payment_method TEXT,
            payment_provider TEXT,
            payment_mode TEXT,
            paid_at TEXT,
            classification TEXT NOT NULL DEFAULT 'unknown',
            classification_reason TEXT,
            is_test INTEGER,
            test_reason TEXT,
            checkout_id TEXT,
            checkout_started_at TEXT,
            checkout_environment TEXT,
            attribution_json TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    order_v2_columns = {
        "schema_version": "TEXT NOT NULL DEFAULT 'int-002.v1'",
        "currency": "TEXT",
        "total_net": "REAL",
        "tax_total": "REAL",
        "payment_status": "TEXT",
        "payment_method": "TEXT",
        "payment_provider": "TEXT",
        "payment_mode": "TEXT",
        "paid_at": "TEXT",
        "classification": "TEXT NOT NULL DEFAULT 'unknown'",
        "classification_reason": "TEXT",
        "is_test": "INTEGER",
        "test_reason": "TEXT",
        "checkout_id": "TEXT",
        "checkout_started_at": "TEXT",
        "checkout_environment": "TEXT",
        "attribution_json": "TEXT NOT NULL DEFAULT '{}'",
    }
    try:
        existing_order_columns = {
            row[1] for row in conn.execute("PRAGMA table_info(orders)").fetchall()
        }
        for column_name, column_type in order_v2_columns.items():
            if column_name not in existing_order_columns:
                conn.execute(
                    f"ALTER TABLE orders ADD COLUMN {column_name} {column_type}"
                )
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(
            "[DB] INT-002 v2 migration failed: %s", e
        )
        raise
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_orders_status
        ON orders(status)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_orders_created_at
        ON orders(created_at)
    """)
    conn.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_orders_checkout_id
        ON orders(checkout_id)
        WHERE checkout_id IS NOT NULL AND checkout_id != ''
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

    conn.execute("""
        CREATE TABLE IF NOT EXISTS analytics_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            period TEXT NOT NULL,
            generated_at TEXT NOT NULL,
            sync_status TEXT NOT NULL,
            sources_json TEXT NOT NULL DEFAULT '{}',
            errors_json TEXT NOT NULL DEFAULT '[]',
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_analytics_snapshots_period
        ON analytics_snapshots(period, created_at DESC)
    """)

    # Append-only legacy revenue classification audit (REV-R0-02).
    conn.execute("""
        CREATE TABLE IF NOT EXISTS revenue_classification_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL
                CHECK (entity_type IN ('order', 'lead', 'portal_qual_lead')),
            entity_key TEXT NOT NULL,
            classification TEXT NOT NULL
                CHECK (classification IN ('real', 'test', 'unknown')),
            reason_code TEXT NOT NULL,
            evidence_json TEXT NOT NULL DEFAULT '{}',
            classified_at TEXT NOT NULL,
            classified_by TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_revenue_classification_entity
        ON revenue_classification_events(entity_type, entity_key, id DESC)
    """)

    # COI Commander control plane
    conn.execute("""
        CREATE TABLE IF NOT EXISTS commander_audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            actor_id TEXT NOT NULL,
            actor_role TEXT NOT NULL,
            action TEXT NOT NULL,
            source TEXT NOT NULL,
            target_type TEXT,
            target_id TEXT,
            before_json TEXT,
            after_json TEXT,
            reason TEXT,
            risk_tier TEXT,
            session_id TEXT,
            prev_hash TEXT,
            row_hash TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_commander_audit_ts
        ON commander_audit_log(ts DESC)
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS commander_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            severity TEXT NOT NULL DEFAULT 'CRITICAL',
            status TEXT NOT NULL DEFAULT 'open',
            source TEXT NOT NULL DEFAULT 'telegram',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS commander_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_type TEXT NOT NULL,
            feedback_type TEXT NOT NULL,
            payload_json TEXT,
            actor_id TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS commander_agent_state (
            agent_id TEXT PRIMARY KEY,
            status TEXT NOT NULL DEFAULT 'LIVE',
            last_run_at TEXT,
            last_error TEXT,
            expected_interval_seconds INTEGER NOT NULL DEFAULT 3600,
            held_count INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS commander_settings (
            key TEXT PRIMARY KEY,
            value_json TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS commander_deeplinks (
            token_hash TEXT PRIMARY KEY,
            ticket_id INTEGER NOT NULL,
            expires_at TEXT NOT NULL,
            used_at TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS commander_login_codes (
            code_hash TEXT PRIMARY KEY,
            sub TEXT NOT NULL,
            role TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            used_at TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS commander_daily_actions (
            action_date TEXT NOT NULL,
            action_count INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (action_date)
        )
    """)

    # Widget customer-chat history (REV-DEMAND-02) — survives process restart
    # created_at: OPS-AI-01 durable AI-ops clock (set once on insert)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS widget_chat_sessions (
            session_id TEXT PRIMARY KEY,
            history_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_widget_chat_updated
        ON widget_chat_sessions(updated_at)
    """)

    _migrate_content_calendar_columns(conn)
    _migrate_commander_calendar_version(conn)
    _migrate_commander_feedback_confidence(conn)
    _migrate_leads_disposition(conn)
    _migrate_widget_chat_created_at(conn)
    _init_marketing_dtl_schema(conn)
    _init_marketing_f1_schema(conn)
    _init_marketing_governance_schema(conn)

    conn.commit()


def _init_marketing_dtl_schema(conn: sqlite3.Connection) -> None:
    """MKT-BRAIN-PRO F0 — Data Truth Layer tables (idempotent)."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS marketing_raw_ingest (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            fetched_at TEXT NOT NULL,
            checksum TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            window_label TEXT,
            status TEXT NOT NULL DEFAULT 'ok',
            error_message TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_marketing_raw_source_fetched
        ON marketing_raw_ingest(source, fetched_at DESC)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_marketing_raw_checksum
        ON marketing_raw_ingest(source, checksum)
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS marketing_facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_key TEXT NOT NULL,
            channel TEXT NOT NULL DEFAULT 'unknown',
            window_label TEXT NOT NULL,
            value REAL NOT NULL,
            confidence REAL NOT NULL DEFAULT 1.0,
            as_of TEXT NOT NULL,
            source_ingest_id INTEGER,
            dims_json TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL,
            UNIQUE(metric_key, channel, window_label, as_of)
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_marketing_facts_key_asof
        ON marketing_facts(metric_key, as_of DESC)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_marketing_facts_channel
        ON marketing_facts(channel, window_label, as_of DESC)
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS data_quality_flags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flag_type TEXT NOT NULL,
            source TEXT NOT NULL,
            severity TEXT NOT NULL DEFAULT 'amber',
            message TEXT NOT NULL,
            details_json TEXT NOT NULL DEFAULT '{}',
            active INTEGER NOT NULL DEFAULT 1,
            as_of TEXT NOT NULL,
            resolved_at TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_data_quality_active
        ON data_quality_flags(active, severity, as_of DESC)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_data_quality_source
        ON data_quality_flags(source, active, as_of DESC)
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS order_margin_facts (
            order_id TEXT PRIMARY KEY,
            gross REAL NOT NULL,
            cogs REAL NOT NULL,
            shipping REAL NOT NULL DEFAULT 0,
            refunds_alloc REAL NOT NULL DEFAULT 0,
            net_margin REAL NOT NULL,
            net_margin_pct REAL NOT NULL,
            cogs_method TEXT NOT NULL DEFAULT 'playbook_60pct',
            attribution_channel TEXT,
            as_of TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_order_margin_asof
        ON order_margin_facts(as_of DESC)
    """)


def _init_marketing_f1_schema(conn: sqlite3.Connection) -> None:
    """MKT-BRAIN-PRO F1 — shadow log, hypotheses, brain_events (idempotent)."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS marketing_shadow_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_id TEXT NOT NULL UNIQUE,
            observed_facts_ref TEXT,
            proposed_action TEXT NOT NULL,
            heuristic_rule_id TEXT NOT NULL,
            llm_rationale_nl TEXT,
            would_execute INTEGER NOT NULL DEFAULT 0,
            governance_result TEXT NOT NULL DEFAULT 'review',
            mb_mode TEXT NOT NULL DEFAULT 'shadow',
            hitl_status TEXT NOT NULL DEFAULT 'pending',
            payload_json TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_marketing_shadow_created
        ON marketing_shadow_log(created_at DESC)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_marketing_shadow_hitl
        ON marketing_shadow_log(hitl_status, created_at DESC)
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS marketing_hypotheses (
            hypothesis_id TEXT PRIMARY KEY,
            statement TEXT NOT NULL,
            proposed_action_ref TEXT,
            status TEXT NOT NULL DEFAULT 'open',
            review_at TEXT,
            outcome TEXT,
            learnings_nl TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_marketing_hypotheses_status
        ON marketing_hypotheses(status, review_at)
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS brain_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            source_brain TEXT NOT NULL,
            payload_json TEXT NOT NULL DEFAULT '{}',
            correlation_id TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            attempts INTEGER NOT NULL DEFAULT 0,
            error_message TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            processed_at TEXT
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_brain_events_status
        ON brain_events(status, created_at)
    """)


def _init_marketing_governance_schema(conn: sqlite3.Connection) -> None:
    """MKT-BRAIN-PRO F2 — approval tokens + circuit breaker events."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS marketing_approval_tokens (
            token_hash TEXT PRIMARY KEY,
            action_id TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            used_at TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_marketing_approval_action
        ON marketing_approval_tokens(action_id)
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS circuit_breaker_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            breaker_id TEXT NOT NULL,
            message TEXT NOT NULL,
            action_id TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_circuit_breaker_created
        ON circuit_breaker_events(created_at DESC)
    """)


def _migrate_widget_chat_created_at(conn: sqlite3.Connection) -> None:
    """OPS-AI-01: durable created_at for widget AI-ops counting (v1.1)."""
    try:
        conn.execute("ALTER TABLE widget_chat_sessions ADD COLUMN created_at TEXT")
    except sqlite3.OperationalError:
        pass
    # Backfill legacy rows: first durable clock we have is updated_at
    conn.execute(
        """
        UPDATE widget_chat_sessions
        SET created_at = updated_at
        WHERE created_at IS NULL OR created_at = ''
        """
    )
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_widget_chat_created
        ON widget_chat_sessions(created_at)
    """)


def _migrate_leads_disposition(conn: sqlite3.Connection) -> None:
    """Add sales HITL disposition on leads (open|acked|closed|snoozed)."""
    try:
        conn.execute(
            "ALTER TABLE leads ADD COLUMN disposition TEXT NOT NULL DEFAULT 'open'"
        )
    except sqlite3.OperationalError:
        pass


def _migrate_content_calendar_columns(conn: sqlite3.Connection) -> None:
    """Add INT-011 publish columns (idempotent)."""
    new_columns = (
        ("publish_result", "TEXT"),
        ("media_url", "TEXT"),
        ("fb_post_id", "TEXT"),
        ("scheduled_publish_at", "TEXT"),
        ("content_type", "TEXT DEFAULT 'text'"),
        ("media_source", "TEXT"),
    )
    for column_name, column_type in new_columns:
        try:
            conn.execute(
                f"ALTER TABLE content_calendar ADD COLUMN {column_name} {column_type}"
            )
        except sqlite3.OperationalError:
            pass


def _migrate_commander_calendar_version(conn: sqlite3.Connection) -> None:
    """Add optimistic-lock version column for calendar entries."""
    try:
        conn.execute("ALTER TABLE content_calendar ADD COLUMN version INTEGER NOT NULL DEFAULT 1")
    except sqlite3.OperationalError:
        pass


def _migrate_commander_feedback_confidence(conn: sqlite3.Connection) -> None:
    try:
        conn.execute("ALTER TABLE commander_feedback ADD COLUMN confidence REAL")
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
                if order_data.get("schema_version") == "int-002.v2":
                    conn.execute(
                        """
                        UPDATE orders SET
                            status = ?,
                            items_json = ?,
                            customer_email = ?,
                            customer_name = ?,
                            total_gross = ?,
                            payment_id = ?,
                            schema_version = ?,
                            currency = ?,
                            total_net = ?,
                            tax_total = ?,
                            payment_status = ?,
                            payment_method = ?,
                            payment_provider = ?,
                            payment_mode = ?,
                            paid_at = ?,
                            classification = ?,
                            classification_reason = ?,
                            is_test = ?,
                            test_reason = ?,
                            checkout_id = ?,
                            checkout_started_at = ?,
                            checkout_environment = ?,
                            attribution_json = ?,
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
                            order_data["schema_version"],
                            order_data.get("currency"),
                            order_data.get("total_net"),
                            order_data.get("tax_total"),
                            order_data.get("payment_status"),
                            order_data.get("payment_method"),
                            order_data.get("payment_provider"),
                            order_data.get("payment_mode"),
                            order_data.get("paid_at"),
                            order_data.get("classification", "unknown"),
                            order_data.get("classification_reason"),
                            _optional_bool_to_int(order_data.get("is_test")),
                            order_data.get("test_reason"),
                            order_data.get("checkout_id"),
                            order_data.get("checkout_started_at"),
                            order_data.get("checkout_environment"),
                            json.dumps(order_data.get("attribution") or {}),
                            now,
                            order_id,
                        ),
                    )
                else:
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
                        total_gross, payment_id, schema_version,
                        currency, total_net, tax_total,
                        payment_status, payment_method, payment_provider,
                        payment_mode, paid_at,
                        classification, classification_reason,
                        is_test, test_reason,
                        checkout_id, checkout_started_at, checkout_environment,
                        attribution_json,
                        created_at, updated_at
                    ) VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                    """,
                    (
                        order_id,
                        order_data["status"],
                        json.dumps(items),
                        customer.get("email"),
                        customer.get("name"),
                        order_data["total_gross"],
                        order_data.get("payment_id"),
                        order_data.get("schema_version", "int-002.v1"),
                        order_data.get("currency"),
                        order_data.get("total_net"),
                        order_data.get("tax_total"),
                        order_data.get("payment_status"),
                        order_data.get("payment_method"),
                        order_data.get("payment_provider"),
                        order_data.get("payment_mode"),
                        order_data.get("paid_at"),
                        order_data.get("classification", "unknown"),
                        order_data.get("classification_reason"),
                        _optional_bool_to_int(order_data.get("is_test")),
                        order_data.get("test_reason"),
                        order_data.get("checkout_id"),
                        order_data.get("checkout_started_at"),
                        order_data.get("checkout_environment"),
                        json.dumps(order_data.get("attribution") or {}),
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


def _optional_bool_to_int(value: Any) -> Optional[int]:
    """Convert nullable producer classification to SQLite representation."""
    if value is None:
        return None
    return int(bool(value))


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
    if order.get("attribution_json"):
        try:
            order["attribution"] = json.loads(order["attribution_json"])
        except Exception:
            order["attribution"] = {}
    else:
        order["attribution"] = {}
    order.pop("attribution_json", None)
    if order.get("is_test") is not None:
        order["is_test"] = bool(order["is_test"])
    order["customer"] = {
        "email": order.pop("customer_email", None),
        "name": order.pop("customer_name", None),
    }
    return order


# ============================================================================
# WIDGET CHAT SESSIONS (REV-DEMAND-02)
# ============================================================================

WIDGET_CHAT_SESSION_TTL_SEC = 24 * 3600


def _widget_session_expired(updated_at: str, ttl_sec: int) -> bool:
    try:
        ts = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        age = (datetime.now(timezone.utc) - ts).total_seconds()
        return age > ttl_sec
    except (TypeError, ValueError):
        return True


def db_save_widget_chat_history(session_id: str, history: List[Dict]) -> None:
    """Upsert widget chat message history (JSON list of {role, content}).

    created_at is set only on first insert (OPS-AI-01 AI-ops clock).
    """
    sid = (session_id or "").strip()
    if not sid:
        return
    now = datetime.now(timezone.utc).isoformat()
    payload = json.dumps(history if isinstance(history, list) else [], ensure_ascii=False)
    with db_transaction() as conn:
        conn.execute(
            """
            INSERT INTO widget_chat_sessions (session_id, history_json, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                history_json = excluded.history_json,
                updated_at = excluded.updated_at
            """,
            (sid[:128], payload, now, now),
        )


def db_get_widget_chat_history(
    session_id: str,
    ttl_sec: int = WIDGET_CHAT_SESSION_TTL_SEC,
) -> Optional[List[Dict]]:
    """Load history if present and not past TTL; deletes expired rows."""
    sid = (session_id or "").strip()
    if not sid:
        return None
    conn = get_connection()
    row = conn.execute(
        "SELECT history_json, updated_at FROM widget_chat_sessions WHERE session_id = ?",
        (sid[:128],),
    ).fetchone()
    if not row:
        return None
    if _widget_session_expired(row["updated_at"], ttl_sec):
        db_delete_widget_chat_history(sid)
        return None
    try:
        data = json.loads(row["history_json"])
    except json.JSONDecodeError:
        return None
    if not isinstance(data, list):
        return None
    return data


def db_delete_widget_chat_history(session_id: str) -> None:
    sid = (session_id or "").strip()
    if not sid:
        return
    conn = get_connection()
    conn.execute(
        "DELETE FROM widget_chat_sessions WHERE session_id = ?",
        (sid[:128],),
    )
    conn.commit()


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
    lead["disposition"] = lead.get("disposition") or "open"
    return lead


_VALID_LEAD_DISPOSITIONS = frozenset({"open", "acked", "closed", "snoozed"})


def db_update_lead_disposition(lead_id: int, disposition: str) -> bool:
    """Set lead disposition for Commander sales HITL. Returns True if updated."""
    disp = (disposition or "").strip().lower()
    if disp not in _VALID_LEAD_DISPOSITIONS:
        return False
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            UPDATE leads
            SET disposition = ?, updated_at = ?
            WHERE id = ?
            """,
            (disp, now, lead_id),
        )
        conn.commit()
        return cur.rowcount > 0
    except Exception:
        conn.rollback()
        return False


# ============================================================================
# Content calendar operations (INT-010)
# ============================================================================

_VALID_CALENDAR_STATUSES = frozenset(
    {"draft", "pending_approval", "approved", "published", "cancelled", "failed", "held"}
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
                source_order_id, media_url, scheduled_publish_at,
                content_type, media_source, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                platform,
                entry_data["title"],
                entry_data["body_nl"],
                entry_data["scheduled_at"],
                entry_data.get("status", "draft"),
                entry_data.get("source_order_id"),
                entry_data.get("media_url"),
                entry_data.get("scheduled_publish_at"),
                entry_data.get("content_type", "text"),
                entry_data.get("media_source"),
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

    query += " ORDER BY COALESCE(scheduled_publish_at, scheduled_at) ASC LIMIT ?"
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
        "content_type",
        "media_source",
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


def db_save_analytics_snapshot(snapshot: Dict) -> Optional[int]:
    """Persist GA4 snapshot row (INT-009 history). Returns internal id."""
    import json
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO analytics_snapshots
            (period, generated_at, sync_status, sources_json, errors_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot["period"],
                snapshot["generated_at"],
                snapshot["sync_status"],
                json.dumps(snapshot.get("sources", {})),
                json.dumps(snapshot.get("errors", [])),
                now,
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)
    except Exception as e:
        conn.rollback()
        import logging
        logging.getLogger(__name__).error("[DB] analytics snapshot save failed: %s", e)
        return None


def db_get_latest_analytics_snapshot(period: Optional[str] = None) -> Optional[Dict]:
    """Return most recent persisted analytics snapshot, optionally filtered by period label."""
    conn = get_connection()
    if period:
        row = conn.execute(
            """
            SELECT * FROM analytics_snapshots
            WHERE period = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (period,),
        ).fetchone()
    else:
        row = conn.execute(
            """
            SELECT * FROM analytics_snapshots
            ORDER BY created_at DESC
            LIMIT 1
            """
        ).fetchone()
    return dict(row) if row else None


def db_list_analytics_snapshots(limit: int = 30) -> List[Dict]:
    """List recent analytics snapshots newest first."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT id, period, generated_at, sync_status, sources_json, errors_json, created_at
        FROM analytics_snapshots
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [dict(row) for row in rows]


# ============================================================================
# Commander control plane (COI Commander)
# ============================================================================

def db_commander_insert_audit(row: Dict) -> Optional[int]:
    """Append-only audit log insert. Returns row id."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO commander_audit_log (
                ts, actor_id, actor_role, action, source,
                target_type, target_id, before_json, after_json,
                reason, risk_tier, session_id, prev_hash, row_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["ts"],
                row["actor_id"],
                row["actor_role"],
                row["action"],
                row["source"],
                row.get("target_type"),
                row.get("target_id"),
                row.get("before_json"),
                row.get("after_json"),
                row.get("reason"),
                row.get("risk_tier"),
                row.get("session_id"),
                row.get("prev_hash"),
                row["row_hash"],
            ),
        )
        conn.commit()
        return cursor.lastrowid
    except Exception:
        conn.rollback()
        return None


def db_commander_list_audit(limit: int = 100, offset: int = 0) -> List[Dict]:
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT * FROM commander_audit_log
        ORDER BY id DESC
        LIMIT ? OFFSET ?
        """,
        (limit, offset),
    ).fetchall()
    return [dict(r) for r in rows]


def db_commander_last_audit_hash() -> Optional[str]:
    conn = get_connection()
    row = conn.execute(
        "SELECT row_hash FROM commander_audit_log ORDER BY id DESC LIMIT 1"
    ).fetchone()
    return row["row_hash"] if row else None


def db_commander_create_ticket(
    title: str,
    description: str,
    source: str = "telegram",
    severity: str = "CRITICAL",
) -> Optional[int]:
    now = datetime.now(timezone.utc).isoformat()
    sev = (severity or "CRITICAL").upper()
    if sev not in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        sev = "CRITICAL"
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO commander_tickets (title, description, severity, status, source, created_at, updated_at)
            VALUES (?, ?, ?, 'open', ?, ?, ?)
            """,
            (title, description, sev, source, now, now),
        )
        conn.commit()
        return cursor.lastrowid
    except Exception:
        conn.rollback()
        return None


def db_commander_get_ticket(ticket_id: int) -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM commander_tickets WHERE id = ?", (ticket_id,)).fetchone()
    return dict(row) if row else None


def db_commander_update_ticket_status(ticket_id: int, status: str) -> bool:
    """HITL disposition for Commander tickets (acked / snoozed / closed / open)."""
    allowed = {"open", "acked", "snoozed", "closed"}
    if status not in allowed:
        return False
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            UPDATE commander_tickets
            SET status = ?, updated_at = ?
            WHERE id = ?
            """,
            (status, now, ticket_id),
        )
        conn.commit()
        return cur.rowcount > 0
    except Exception:
        conn.rollback()
        return False


def db_commander_list_tickets(status: Optional[str] = None, limit: int = 50) -> List[Dict]:
    conn = get_connection()
    if status:
        rows = conn.execute(
            "SELECT * FROM commander_tickets WHERE status = ? ORDER BY created_at DESC LIMIT ?",
            (status, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM commander_tickets ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def db_commander_save_deeplink(token_hash: str, ticket_id: int, expires_at: str) -> bool:
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO commander_deeplinks (token_hash, ticket_id, expires_at, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (token_hash, ticket_id, expires_at, now),
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False


def db_commander_get_deeplink(token_hash: str) -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM commander_deeplinks WHERE token_hash = ?",
        (token_hash,),
    ).fetchone()
    return dict(row) if row else None


def db_commander_mark_deeplink_used(token_hash: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    conn.execute(
        "UPDATE commander_deeplinks SET used_at = ? WHERE token_hash = ?",
        (now, token_hash),
    )
    conn.commit()


def db_commander_save_login_code(
    code_hash: str,
    sub: str,
    role: str,
    expires_at: str,
) -> bool:
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO commander_login_codes
                (code_hash, sub, role, expires_at, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (code_hash, sub, role, expires_at, now),
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False


def db_commander_get_login_code(code_hash: str) -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM commander_login_codes WHERE code_hash = ?",
        (code_hash,),
    ).fetchone()
    return dict(row) if row else None


def db_commander_mark_login_code_used(code_hash: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    conn.execute(
        "UPDATE commander_login_codes SET used_at = ? WHERE code_hash = ?",
        (now, code_hash),
    )
    conn.commit()


def db_commander_insert_feedback(
    action_type: str,
    feedback_type: str,
    payload_json: Optional[str],
    actor_id: Optional[str],
    confidence: Optional[float] = None,
) -> Optional[int]:
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO commander_feedback (
                action_type, feedback_type, payload_json, actor_id, created_at, confidence
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (action_type, feedback_type, payload_json, actor_id, now, confidence),
        )
        conn.commit()
        return cursor.lastrowid
    except Exception:
        conn.rollback()
        return None


def db_commander_feedback_stats(action_type: str, days: int = 30) -> Dict:
    """Rolling stats for graduation thresholds."""
    conn = get_connection()
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    rows = conn.execute(
        """
        SELECT feedback_type, COUNT(*) AS cnt
        FROM commander_feedback
        WHERE action_type = ? AND created_at >= ?
        GROUP BY feedback_type
        """,
        (action_type, since),
    ).fetchall()
    stats = {r["feedback_type"]: r["cnt"] for r in rows}
    conf_row = conn.execute(
        """
        SELECT AVG(confidence) AS avg_conf
        FROM commander_feedback
        WHERE action_type = ? AND created_at >= ? AND confidence IS NOT NULL
        """,
        (action_type, since),
    ).fetchone()
    total = sum(stats.values()) or 1
    overrides = stats.get("rejection", 0) + stats.get("correction", 0)
    approvals = stats.get("approval", 0)
    confidence_avg = round(float(conf_row["avg_conf"] or 0), 3) if conf_row else 0.0
    return {
        "action_type": action_type,
        "total": total,
        "approvals": approvals,
        "overrides": overrides,
        "override_rate_pct": round(overrides / total * 100, 2),
        "approved_without_edit": approvals,
        "confidence_avg": confidence_avg,
    }


def db_commander_get_setting(key: str) -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM commander_settings WHERE key = ?", (key,)).fetchone()
    return dict(row) if row else None


def db_commander_set_setting(key: str, value_json: str) -> bool:
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO commander_settings (key, value_json, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET value_json = excluded.value_json, updated_at = excluded.updated_at
            """,
            (key, value_json, now),
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False


def db_commander_upsert_agent_state(agent_id: str, updates: Dict) -> bool:
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    existing = conn.execute(
        "SELECT agent_id FROM commander_agent_state WHERE agent_id = ?",
        (agent_id,),
    ).fetchone()
    if existing:
        allowed = {"status", "last_run_at", "last_error", "expected_interval_seconds", "held_count"}
        filtered = {k: v for k, v in updates.items() if k in allowed}
        if not filtered:
            return True
        filtered["updated_at"] = now
        set_clause = ", ".join(f"{k} = ?" for k in filtered)
        conn.execute(
            f"UPDATE commander_agent_state SET {set_clause} WHERE agent_id = ?",
            list(filtered.values()) + [agent_id],
        )
    else:
        conn.execute(
            """
            INSERT INTO commander_agent_state (
                agent_id, status, last_run_at, last_error,
                expected_interval_seconds, held_count, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                agent_id,
                updates.get("status", "LIVE"),
                updates.get("last_run_at"),
                updates.get("last_error"),
                updates.get("expected_interval_seconds", 3600),
                updates.get("held_count", 0),
                now,
            ),
        )
    conn.commit()
    return True


def db_commander_list_agent_states() -> List[Dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM commander_agent_state ORDER BY agent_id").fetchall()
    return [dict(r) for r in rows]


def db_commander_get_agent_state(agent_id: str) -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM commander_agent_state WHERE agent_id = ?",
        (agent_id,),
    ).fetchone()
    return dict(row) if row else None


# ============================================================================
# Revenue classification audit (REV-R0-02)
# ============================================================================

def db_record_revenue_classification(
    entity_type: str,
    entity_key: str,
    classification: str,
    reason_code: str,
    evidence: Optional[Dict[str, Any]] = None,
    classified_by: str = "rule:revenue_event.v1",
) -> Optional[int]:
    """Append a classification unless the latest value is identical."""
    if entity_type not in {"order", "lead", "portal_qual_lead"}:
        raise ValueError("invalid revenue classification entity_type")
    if classification not in {"real", "test", "unknown"}:
        raise ValueError("invalid revenue classification")
    if not entity_key or not reason_code:
        raise ValueError("entity_key and reason_code are required")

    evidence_json = json.dumps(evidence or {}, sort_keys=True)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    conn = get_connection()
    latest = conn.execute(
        """
        SELECT id, classification, reason_code, evidence_json, classified_by
        FROM revenue_classification_events
        WHERE entity_type = ? AND entity_key = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (entity_type, entity_key),
    ).fetchone()
    if latest and (
        latest["classification"] == classification
        and latest["reason_code"] == reason_code
        and latest["evidence_json"] == evidence_json
        and latest["classified_by"] == classified_by
    ):
        return int(latest["id"])

    try:
        cursor = conn.execute(
            """
            INSERT INTO revenue_classification_events (
                entity_type, entity_key, classification, reason_code,
                evidence_json, classified_at, classified_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entity_type,
                entity_key,
                classification,
                reason_code,
                evidence_json,
                now,
                classified_by,
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)
    except Exception:
        conn.rollback()
        raise


def db_get_revenue_classification(entity_type: str, entity_key: str) -> Optional[Dict]:
    """Return the latest append-only classification for one legacy entity."""
    conn = get_connection()
    row = conn.execute(
        """
        SELECT id, entity_type, entity_key, classification, reason_code,
               evidence_json, classified_at, classified_by
        FROM revenue_classification_events
        WHERE entity_type = ? AND entity_key = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (entity_type, entity_key),
    ).fetchone()
    if not row:
        return None
    result = dict(row)
    result["evidence"] = json.loads(result.pop("evidence_json") or "{}")
    return result


def db_list_revenue_classifications() -> List[Dict]:
    """Return only the latest classification per entity."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT event.id, event.entity_type, event.entity_key, event.classification,
               event.reason_code, event.evidence_json, event.classified_at,
               event.classified_by
        FROM revenue_classification_events AS event
        JOIN (
            SELECT entity_type, entity_key, MAX(id) AS latest_id
            FROM revenue_classification_events
            GROUP BY entity_type, entity_key
        ) AS latest ON latest.latest_id = event.id
        ORDER BY event.entity_type, event.entity_key
        """
    ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["evidence"] = json.loads(item.pop("evidence_json") or "{}")
        result.append(item)
    return result


def db_list_orders(limit: int = 50) -> List[Dict]:
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT orders.order_id, orders.status, orders.total_gross,
               orders.customer_name, orders.customer_email,
               orders.created_at, orders.updated_at,
               classification.classification,
               classification.reason_code AS classification_reason
        FROM orders
        LEFT JOIN revenue_classification_events AS classification
          ON classification.id = (
              SELECT MAX(latest.id)
              FROM revenue_classification_events AS latest
              WHERE latest.entity_type = 'order'
                AND latest.entity_key = orders.order_id
          )
        ORDER BY orders.created_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["classification"] = item.get("classification") or "unknown"
        item["is_test"] = (
            True
            if item["classification"] == "test"
            else False if item["classification"] == "real" else None
        )
        result.append(item)
    return result


def db_list_leads(limit: int = 50) -> List[Dict]:
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT leads.id, leads.email, leads.name, leads.source,
               leads.game_score, leads.reward_tier,
               leads.disposition,
               leads.created_at, leads.updated_at,
               classification.classification,
               classification.reason_code AS classification_reason
        FROM leads
        LEFT JOIN revenue_classification_events AS classification
          ON classification.id = (
              SELECT MAX(latest.id)
              FROM revenue_classification_events AS latest
              WHERE latest.entity_type = 'lead'
                AND latest.entity_key = CAST(leads.id AS TEXT)
          )
        ORDER BY leads.created_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["classification"] = item.get("classification") or "unknown"
        item["disposition"] = item.get("disposition") or "open"
        item["is_test"] = (
            True
            if item["classification"] == "test"
            else False if item["classification"] == "real" else None
        )
        result.append(item)
    return result


def db_update_calendar_entry_versioned(
    entry_id: int,
    updates: Dict,
    expected_version: int,
) -> tuple[bool, Optional[int]]:
    """Optimistic lock update. Returns (success, new_version)."""
    allowed = {
        "platform", "title", "body_nl", "scheduled_at", "status",
        "source_order_id", "publish_result", "media_url", "fb_post_id",
        "scheduled_publish_at", "content_type", "media_source",
    }
    filtered = {k: v for k, v in updates.items() if k in allowed and v is not None}
    if not filtered:
        return True, expected_version
    if "status" in filtered and filtered["status"] not in _VALID_CALENDAR_STATUSES:
        return False, None

    new_version = expected_version + 1
    filtered["updated_at"] = datetime.now(timezone.utc).isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in filtered)
    values = list(filtered.values()) + [new_version, entry_id, expected_version]

    conn = get_connection()
    try:
        cursor = conn.execute(
            f"""
            UPDATE content_calendar
            SET {set_clause}, version = ?
            WHERE id = ? AND COALESCE(version, 1) = ?
            """,
            values,
        )
        conn.commit()
        if cursor.rowcount == 0:
            return False, None
        return True, new_version
    except Exception:
        conn.rollback()
        return False, None


def db_commander_increment_daily_actions() -> int:
    """Increment daily human action counter; returns new count."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO commander_daily_actions (action_date, action_count)
        VALUES (?, 1)
        ON CONFLICT(action_date) DO UPDATE SET action_count = action_count + 1
        """,
        (today,),
    )
    conn.commit()
    row = conn.execute(
        "SELECT action_count FROM commander_daily_actions WHERE action_date = ?",
        (today,),
    ).fetchone()
    return row["action_count"] if row else 1


def db_commander_get_daily_actions() -> int:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    conn = get_connection()
    row = conn.execute(
        "SELECT action_count FROM commander_daily_actions WHERE action_date = ?",
        (today,),
    ).fetchone()
    return row["action_count"] if row else 0


def db_count_calendar_by_status(status: str) -> int:
    conn = get_connection()
    row = conn.execute(
        "SELECT COUNT(*) AS cnt FROM content_calendar WHERE status = ?",
        (status,),
    ).fetchone()
    return row["cnt"] if row else 0


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


# ============================================================================
# Marketing Data Truth Layer (MKT-BRAIN-PRO F0)
# ============================================================================


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def db_insert_marketing_raw_ingest(row: Dict) -> Optional[int]:
    """Append-only raw marketing ingest. Returns row id."""
    now = _utc_now_iso()
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO marketing_raw_ingest
            (source, fetched_at, checksum, payload_json, window_label,
             status, error_message, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["source"],
                row["fetched_at"],
                row["checksum"],
                json.dumps(row.get("payload", {})),
                row.get("window_label"),
                row.get("status", "ok"),
                row.get("error_message"),
                now,
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)
    except Exception as e:
        conn.rollback()
        import logging
        logging.getLogger(__name__).error("[DB] marketing_raw_ingest insert failed: %s", e)
        return None


def db_get_latest_marketing_raw_ingest(source: str) -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute(
        """
        SELECT * FROM marketing_raw_ingest
        WHERE source = ?
        ORDER BY fetched_at DESC, id DESC
        LIMIT 1
        """,
        (source,),
    ).fetchone()
    if not row:
        return None
    item = dict(row)
    try:
        item["payload"] = json.loads(item.pop("payload_json") or "{}")
    except Exception:
        item["payload"] = {}
    return item


def db_find_marketing_raw_by_checksum(source: str, checksum: str) -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute(
        """
        SELECT id, source, fetched_at, checksum, status
        FROM marketing_raw_ingest
        WHERE source = ? AND checksum = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (source, checksum),
    ).fetchone()
    return dict(row) if row else None


def db_upsert_marketing_fact(fact: Dict) -> Optional[int]:
    """Upsert normalized marketing fact by unique key tuple."""
    now = _utc_now_iso()
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO marketing_facts
            (metric_key, channel, window_label, value, confidence, as_of,
             source_ingest_id, dims_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(metric_key, channel, window_label, as_of) DO UPDATE SET
                value = excluded.value,
                confidence = excluded.confidence,
                source_ingest_id = excluded.source_ingest_id,
                dims_json = excluded.dims_json
            """,
            (
                fact["metric_key"],
                fact.get("channel", "unknown"),
                fact["window_label"],
                float(fact["value"]),
                float(fact.get("confidence", 1.0)),
                fact["as_of"],
                fact.get("source_ingest_id"),
                json.dumps(fact.get("dims", {})),
                now,
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)
    except Exception as e:
        conn.rollback()
        import logging
        logging.getLogger(__name__).error("[DB] marketing_facts upsert failed: %s", e)
        return None


def db_list_marketing_facts(
    metric_key: Optional[str] = None,
    limit: int = 100,
) -> List[Dict]:
    conn = get_connection()
    if metric_key:
        rows = conn.execute(
            """
            SELECT * FROM marketing_facts
            WHERE metric_key = ?
            ORDER BY as_of DESC, id DESC
            LIMIT ?
            """,
            (metric_key, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT * FROM marketing_facts
            ORDER BY as_of DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        try:
            item["dims"] = json.loads(item.pop("dims_json") or "{}")
        except Exception:
            item["dims"] = {}
        result.append(item)
    return result


def db_get_latest_fact_as_of(metric_key: str, channel: str = "all") -> Optional[str]:
    conn = get_connection()
    row = conn.execute(
        """
        SELECT as_of FROM marketing_facts
        WHERE metric_key = ? AND channel = ?
        ORDER BY as_of DESC
        LIMIT 1
        """,
        (metric_key, channel),
    ).fetchone()
    return row["as_of"] if row else None


def db_deactivate_quality_flags(source: str, flag_type: Optional[str] = None) -> int:
    """Mark active quality flags as resolved for a source (optionally typed)."""
    now = _utc_now_iso()
    conn = get_connection()
    if flag_type:
        cursor = conn.execute(
            """
            UPDATE data_quality_flags
            SET active = 0, resolved_at = ?
            WHERE source = ? AND flag_type = ? AND active = 1
            """,
            (now, source, flag_type),
        )
    else:
        cursor = conn.execute(
            """
            UPDATE data_quality_flags
            SET active = 0, resolved_at = ?
            WHERE source = ? AND active = 1
            """,
            (now, source),
        )
    conn.commit()
    return int(cursor.rowcount or 0)


def db_insert_quality_flag(flag: Dict) -> Optional[int]:
    """Insert a quality flag; deactivates prior active flags of same source+type."""
    now = _utc_now_iso()
    source = flag["source"]
    flag_type = flag["flag_type"]
    db_deactivate_quality_flags(source, flag_type)
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO data_quality_flags
            (flag_type, source, severity, message, details_json, active, as_of, created_at)
            VALUES (?, ?, ?, ?, ?, 1, ?, ?)
            """,
            (
                flag_type,
                source,
                flag.get("severity", "amber"),
                flag["message"],
                json.dumps(flag.get("details", {})),
                flag.get("as_of", now),
                now,
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)
    except Exception as e:
        conn.rollback()
        import logging
        logging.getLogger(__name__).error("[DB] data_quality_flags insert failed: %s", e)
        return None


def db_list_active_quality_flags(limit: int = 100) -> List[Dict]:
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT * FROM data_quality_flags
        WHERE active = 1
        ORDER BY
            CASE severity
                WHEN 'critical' THEN 0
                WHEN 'red' THEN 1
                WHEN 'amber' THEN 2
                ELSE 3
            END,
            as_of DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        try:
            item["details"] = json.loads(item.pop("details_json") or "{}")
        except Exception:
            item["details"] = {}
        result.append(item)
    return result


def db_upsert_order_margin_fact(row: Dict) -> bool:
    now = _utc_now_iso()
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO order_margin_facts
            (order_id, gross, cogs, shipping, refunds_alloc, net_margin, net_margin_pct,
             cogs_method, attribution_channel, as_of, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(order_id) DO UPDATE SET
                gross = excluded.gross,
                cogs = excluded.cogs,
                shipping = excluded.shipping,
                refunds_alloc = excluded.refunds_alloc,
                net_margin = excluded.net_margin,
                net_margin_pct = excluded.net_margin_pct,
                cogs_method = excluded.cogs_method,
                attribution_channel = excluded.attribution_channel,
                as_of = excluded.as_of,
                updated_at = excluded.updated_at
            """,
            (
                row["order_id"],
                float(row["gross"]),
                float(row["cogs"]),
                float(row.get("shipping", 0)),
                float(row.get("refunds_alloc", 0)),
                float(row["net_margin"]),
                float(row["net_margin_pct"]),
                row.get("cogs_method", "playbook_60pct"),
                row.get("attribution_channel"),
                row.get("as_of", now),
                now,
                now,
            ),
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        import logging
        logging.getLogger(__name__).error("[DB] order_margin_facts upsert failed: %s", e)
        return False


def db_get_order_margin_fact(order_id: str) -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM order_margin_facts WHERE order_id = ?",
        (order_id,),
    ).fetchone()
    return dict(row) if row else None


def db_count_order_margin_facts() -> int:
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) AS n FROM order_margin_facts").fetchone()
    return int(row["n"] if row else 0)


def db_count_orders() -> int:
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) AS n FROM orders").fetchone()
    return int(row["n"] if row else 0)


def db_list_orders_full(limit: int = 500) -> List[Dict]:
    """Full order rows with attribution — for DTL ingest (not Commander list)."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT * FROM orders
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [_row_to_order_dict(row) for row in rows]


def db_margin_coverage_stats() -> Dict[str, Any]:
    """Orders vs margin facts coverage for Data Health."""
    conn = get_connection()
    total = int(
        conn.execute("SELECT COUNT(*) AS n FROM orders").fetchone()["n"] or 0
    )
    with_margin = int(
        conn.execute("SELECT COUNT(*) AS n FROM order_margin_facts").fetchone()["n"] or 0
    )
    pct = (with_margin / total * 100.0) if total else 0.0
    return {
        "orders_total": total,
        "margin_facts": with_margin,
        "coverage_pct": round(pct, 2),
    }


# ============================================================================
# Marketing Brain F1 — shadow / hypotheses / brain_events
# ============================================================================


def db_insert_marketing_shadow(row: Dict) -> Optional[int]:
    now = _utc_now_iso()
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO marketing_shadow_log
            (action_id, observed_facts_ref, proposed_action, heuristic_rule_id,
             llm_rationale_nl, would_execute, governance_result, mb_mode,
             hitl_status, payload_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["action_id"],
                row.get("observed_facts_ref"),
                row["proposed_action"],
                row["heuristic_rule_id"],
                row.get("llm_rationale_nl"),
                1 if row.get("would_execute") else 0,
                row.get("governance_result", "review"),
                row.get("mb_mode", "shadow"),
                row.get("hitl_status", "pending"),
                json.dumps(row.get("payload", {})),
                now,
                now,
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)
    except Exception as e:
        conn.rollback()
        import logging
        logging.getLogger(__name__).error("[DB] marketing_shadow_log insert failed: %s", e)
        return None


def db_get_marketing_shadow(action_id: str) -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM marketing_shadow_log WHERE action_id = ?",
        (action_id,),
    ).fetchone()
    if not row:
        return None
    item = dict(row)
    try:
        item["payload"] = json.loads(item.pop("payload_json") or "{}")
    except Exception:
        item["payload"] = {}
    item["would_execute"] = bool(item.get("would_execute"))
    return item


def db_update_marketing_shadow_hitl(
    action_id: str,
    hitl_status: str,
    governance_result: Optional[str] = None,
) -> bool:
    now = _utc_now_iso()
    conn = get_connection()
    try:
        if governance_result:
            conn.execute(
                """
                UPDATE marketing_shadow_log
                SET hitl_status = ?, governance_result = ?, updated_at = ?
                WHERE action_id = ?
                """,
                (hitl_status, governance_result, now, action_id),
            )
        else:
            conn.execute(
                """
                UPDATE marketing_shadow_log
                SET hitl_status = ?, updated_at = ?
                WHERE action_id = ?
                """,
                (hitl_status, now, action_id),
            )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        import logging
        logging.getLogger(__name__).error("[DB] shadow hitl update failed: %s", e)
        return False


def db_list_marketing_shadow(limit: int = 20) -> List[Dict]:
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT * FROM marketing_shadow_log
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        try:
            item["payload"] = json.loads(item.pop("payload_json") or "{}")
        except Exception:
            item["payload"] = {}
        item["would_execute"] = bool(item.get("would_execute"))
        result.append(item)
    return result


def db_insert_marketing_hypothesis(row: Dict) -> bool:
    now = _utc_now_iso()
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO marketing_hypotheses
            (hypothesis_id, statement, proposed_action_ref, status, review_at,
             outcome, learnings_nl, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["hypothesis_id"],
                row["statement"],
                row.get("proposed_action_ref"),
                row.get("status", "open"),
                row.get("review_at"),
                row.get("outcome"),
                row.get("learnings_nl"),
                now,
                now,
            ),
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        import logging
        logging.getLogger(__name__).error("[DB] marketing_hypotheses insert failed: %s", e)
        return False


def db_list_marketing_hypotheses(
    status: Optional[str] = None,
    limit: int = 50,
) -> List[Dict]:
    conn = get_connection()
    if status:
        rows = conn.execute(
            """
            SELECT * FROM marketing_hypotheses
            WHERE status = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (status, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT * FROM marketing_hypotheses
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def db_enqueue_brain_event(event: Dict) -> Optional[int]:
    now = _utc_now_iso()
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO brain_events
            (event_type, source_brain, payload_json, correlation_id,
             status, attempts, created_at, updated_at)
            VALUES (?, ?, ?, ?, 'pending', 0, ?, ?)
            """,
            (
                event["event_type"],
                event.get("source_brain", "mb"),
                json.dumps(event.get("payload", {})),
                event.get("correlation_id"),
                now,
                now,
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)
    except Exception as e:
        conn.rollback()
        import logging
        logging.getLogger(__name__).error("[DB] brain_events enqueue failed: %s", e)
        return None


def db_claim_brain_events(limit: int = 20) -> List[Dict]:
    """Mark pending events as processing and return them."""
    now = _utc_now_iso()
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT * FROM brain_events
        WHERE status = 'pending'
        ORDER BY id ASC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    claimed = []
    for row in rows:
        conn.execute(
            """
            UPDATE brain_events
            SET status = 'processing', attempts = attempts + 1, updated_at = ?
            WHERE id = ? AND status = 'pending'
            """,
            (now, row["id"]),
        )
        item = dict(row)
        try:
            item["payload"] = json.loads(item.pop("payload_json") or "{}")
        except Exception:
            item["payload"] = {}
        claimed.append(item)
    conn.commit()
    return claimed


def db_finish_brain_event(
    event_id: int,
    status: str,
    error_message: Optional[str] = None,
) -> None:
    now = _utc_now_iso()
    conn = get_connection()
    conn.execute(
        """
        UPDATE brain_events
        SET status = ?, error_message = ?, processed_at = ?, updated_at = ?
        WHERE id = ?
        """,
        (status, error_message, now if status in ("done", "dead") else None, now, event_id),
    )
    conn.commit()


def db_rolling_net_margin_pct(limit: int = 50) -> Optional[float]:
    """Average net_margin_pct across recent margin facts (proxy for 7d rolling)."""
    conn = get_connection()
    row = conn.execute(
        """
        SELECT AVG(net_margin_pct) AS avg_pct, COUNT(*) AS n
        FROM (
            SELECT net_margin_pct FROM order_margin_facts
            ORDER BY as_of DESC
            LIMIT ?
        )
        """,
        (limit,),
    ).fetchone()
    if not row or not row["n"]:
        return None
    return float(row["avg_pct"])
