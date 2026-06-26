"""
DEPRECATED (A4-01): JSON session persistence removed. SQLite is the only source of truth.

This script restored session JSON files from backup for the old dual-persistence mode.
Kept in archive/ for reference only.

Original usage:
  python scripts/restore_sessions_from_backup.py [YYYY-MM-DD]
"""

import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
SESSIONS_DIR = BASE / "data" / "sessions"


def main():
    print("DEPRECATED: JSON session mode removed in A4-01 (SQLite-only).")
    print("To restore data, import JSON backups into SQLite via _sync_to_sqlite.")
    sys.exit(1)


if __name__ == "__main__":
    main()
