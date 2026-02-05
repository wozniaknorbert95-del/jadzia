"""
Restore session JSON files from backup (Phase 5 rollback to Phase 4).

Copies *.json from data/sessions/backup_YYYY-MM-DD/ back to data/sessions/.
Run after setting USE_SQLITE_STATE=0 and restarting the app.

Usage:
  python scripts/restore_sessions_from_backup.py [BACKUP_DATE]
  BACKUP_DATE  optional, e.g. 2025-02-04 (default: latest backup_* folder)
"""

import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
SESSIONS_DIR = BASE / "data" / "sessions"


def main():
    backup_date = (sys.argv[1] if len(sys.argv) > 1 else "").strip()
    if backup_date and not backup_date.replace("-", "").isdigit():
        print("Usage: python scripts/restore_sessions_from_backup.py [YYYY-MM-DD]")
        sys.exit(1)

    if not SESSIONS_DIR.exists():
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    if backup_date:
        backup_dir = SESSIONS_DIR / f"backup_{backup_date}"
    else:
        # Latest backup_* by name (assumes YYYY-MM-DD sorts)
        backups = sorted(SESSIONS_DIR.glob("backup_*"))
        if not backups:
            print("No backup_YYYY-MM-DD folder found in data/sessions.")
            sys.exit(1)
        backup_dir = backups[-1]

    if not backup_dir.is_dir():
        print(f"Backup folder not found: {backup_dir}")
        sys.exit(1)

    json_files = list(backup_dir.glob("*.json"))
    if not json_files:
        print(f"No *.json files in {backup_dir}")
        sys.exit(0)

    print(f"Restoring {len(json_files)} file(s) from {backup_dir} to {SESSIONS_DIR}")
    for f in json_files:
        dest = SESSIONS_DIR / f.name
        try:
            dest.write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
            print(f"  {f.name}")
        except Exception as e:
            print(f"  ERROR {f.name}: {e}", file=sys.stderr)
            sys.exit(1)
    print("Done. Set USE_SQLITE_STATE=0 and restart the app for Phase 4 (JSON) mode.")


if __name__ == "__main__":
    main()
