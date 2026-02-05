"""
Backup session JSON files before Phase 5 cutover (SQLite-only).

Creates data/sessions/backup_YYYY-MM-DD/ and copies all *.json files there.
Run once before deploying Phase 5 so rollback can restore from this folder.

Usage:
  python scripts/backup_sessions_json.py [--move] [--date YYYY-MM-DD]
  --move   move files instead of copy (default: copy)
  --date   use this date in folder name (default: today)
"""

import argparse
import json
import shutil
import sys
from datetime import date
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

BASE = Path(__file__).parent.parent
SESSIONS_DIR = BASE / "data" / "sessions"


def main():
    ap = argparse.ArgumentParser(description="Backup session JSON files to data/sessions/backup_YYYY-MM-DD/")
    ap.add_argument("--move", action="store_true", help="Move files instead of copy")
    ap.add_argument("--date", type=str, metavar="YYYY-MM-DD", help="Date for folder name (default: today)")
    args = ap.parse_args()

    use_date = args.date or date.today().isoformat()
    try:
        date.fromisoformat(use_date)
    except ValueError:
        print(f"Invalid --date: {use_date}. Use YYYY-MM-DD.")
        sys.exit(1)

    if not SESSIONS_DIR.exists():
        print(f"Sessions dir does not exist: {SESSIONS_DIR}. Nothing to backup.")
        sys.exit(0)

    backup_dir = SESSIONS_DIR / f"backup_{use_date}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    json_files = list(SESSIONS_DIR.glob("*.json"))
    # Exclude backup subdirs (e.g. backup_2025-02-04)
    json_files = [f for f in json_files if f.is_file() and f.parent == SESSIONS_DIR]

    if not json_files:
        print(f"No *.json files in {SESSIONS_DIR}. Nothing to backup.")
        sys.exit(0)

    op = "Moving" if args.move else "Copying"
    print(f"{op} {len(json_files)} file(s) to {backup_dir}")

    for f in json_files:
        dest = backup_dir / f.name
        try:
            if args.move:
                shutil.move(str(f), str(dest))
            else:
                shutil.copy2(str(f), str(dest))
            print(f"  {f.name}")
        except Exception as e:
            print(f"  ERROR {f.name}: {e}", file=sys.stderr)
            sys.exit(1)

    # Verify: list and spot-check one
    count = len(list(backup_dir.glob("*.json")))
    print(f"Backup complete: {count} file(s) in {backup_dir}")
    if json_files and not args.move:
        sample = backup_dir / json_files[0].name
        try:
            with open(sample, encoding="utf-8") as fp:
                json.load(fp)
            print("Spot-check: one file reads as valid JSON.")
        except Exception as e:
            print(f"Spot-check warning: {e}")


if __name__ == "__main__":
    main()
