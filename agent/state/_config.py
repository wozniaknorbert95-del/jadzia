import logging
from pathlib import Path

_log = logging.getLogger("agent.state")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
SESSIONS_DIR = DATA_DIR / "sessions"
LOCKS_DIR = SESSIONS_DIR / ".locks"
BACKUPS_DIR = DATA_DIR / "backups"
LEGACY_STATE_FILE = DATA_DIR / ".agent_state.json"
LEGACY_LOCK_FILE = DATA_DIR / ".agent.lock"
MIGRATION_MARKER = DATA_DIR / ".migrated"

SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
LOCKS_DIR.mkdir(parents=True, exist_ok=True)
BACKUPS_DIR.mkdir(parents=True, exist_ok=True)


class OperationStatus:
    PLANNING = "planning"
    READING_FILES = "reading_files"
    GENERATING_CODE = "generating_code"
    DIFF_READY = "diff_ready"
    APPROVED = "approved"
    WRITING_FILES = "writing_files"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


TERMINAL_STATUSES = (OperationStatus.COMPLETED, OperationStatus.FAILED, OperationStatus.ROLLED_BACK)
