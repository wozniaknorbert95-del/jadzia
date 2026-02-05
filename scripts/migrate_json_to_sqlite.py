"""
Migrate existing JSON session files to SQLite.

Usage: python scripts/migrate_json_to_sqlite.py [--dry-run]
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.db import (
    db_create_or_update_session,
    db_create_task,
    db_update_task,
    db_set_active_task,
    db_update_task_queue,
    db_get_session,
    db_get_task
)


def parse_session_filename(filename: str) -> tuple:
    """
    Parse session filename to extract chat_id and source.

    Format: {source}_{chat_id}.json
    Example: http_chat_001.json -> ("chat_001", "http")

    Returns:
        (chat_id, source) or None if invalid
    """
    if not filename.endswith('.json'):
        return None

    name = filename[:-5]  # Remove .json

    if '_' not in name:
        return None

    # Split on first underscore
    parts = name.split('_', 1)
    if len(parts) != 2:
        return None

    source, chat_id = parts
    return (chat_id, source)


def migrate_session(filepath: str, dry_run: bool = False) -> dict:
    """
    Migrate one JSON session file to SQLite.

    Returns:
        {
            "success": bool,
            "chat_id": str,
            "source": str,
            "tasks_migrated": int,
            "error": str | None
        }
    """
    filename = os.path.basename(filepath)

    # Parse filename
    parsed = parse_session_filename(filename)
    if not parsed:
        return {
            "success": False,
            "error": f"Invalid filename format: {filename}"
        }

    chat_id, source = parsed

    try:
        # Load JSON
        with open(filepath, 'r', encoding='utf-8') as f:
            state = json.load(f)

        # Normalize to multi-task format if legacy
        if "tasks" not in state and "id" in state:
            # Legacy format - wrap in tasks dict
            task_id = state.get("id")
            state = {
                "chat_id": chat_id,
                "source": source,
                "tasks": {task_id: state},
                "active_task_id": task_id,
                "task_queue": []
            }

        tasks = state.get("tasks", {})
        active_task_id = state.get("active_task_id")
        task_queue = state.get("task_queue", [])

        if dry_run:
            print(f"[DRY-RUN] Would migrate: {chat_id} ({source}) - {len(tasks)} tasks")
            return {
                "success": True,
                "chat_id": chat_id,
                "source": source,
                "tasks_migrated": len(tasks),
                "dry_run": True
            }

        # Check if already migrated
        existing_session = db_get_session(chat_id, source)
        if existing_session:
            print(f"[SKIP] Session already exists: {chat_id} ({source})")
            return {
                "success": True,
                "chat_id": chat_id,
                "source": source,
                "tasks_migrated": 0,
                "skipped": True
            }

        # Create session
        db_create_or_update_session(chat_id, source)

        # Migrate tasks
        tasks_migrated = 0
        for task_id, task_data in tasks.items():
            # Check if task already exists
            existing_task = db_get_task(task_id)
            if existing_task:
                continue

            # Prepare task data
            db_task = {
                "task_id": task_id,
                "chat_id": chat_id,
                "source": source,
                "operation_id": task_data.get("operation_id", task_data.get("id", "")),
                "status": task_data.get("status", "unknown"),
                "user_input": task_data.get("user_input"),
                "dry_run": task_data.get("dry_run", False),
                "webhook_url": task_data.get("webhook_url"),
                "created_at": task_data.get("created_at"),
                "plan": task_data.get("plan"),
                "diffs": task_data.get("diffs"),
                "new_contents": task_data.get("new_contents"),
                "written_files": task_data.get("written_files"),
                "errors": task_data.get("errors", []),
                "pending_plan": task_data.get("pending_plan"),
                "validation_errors": task_data.get("validation_errors"),
                "retry_count": task_data.get("retry_count", 0),
                "deploy_result": task_data.get("deploy_result"),
                "awaiting_response": task_data.get("awaiting_response", False),
                "awaiting_type": task_data.get("awaiting_type"),
                "pending_plan_with_questions": task_data.get("pending_plan_with_questions"),
                "last_response": task_data.get("last_response"),
                "files_to_modify": task_data.get("files_to_modify"),
                "completed_at": task_data.get("completed_at")
            }

            db_create_task(db_task)
            tasks_migrated += 1

        # Set active task and queue
        db_set_active_task(chat_id, source, active_task_id)
        db_update_task_queue(chat_id, source, task_queue)

        print(f"[OK] Migrated: {chat_id} ({source}) - {tasks_migrated} tasks")

        return {
            "success": True,
            "chat_id": chat_id,
            "source": source,
            "tasks_migrated": tasks_migrated
        }

    except Exception as e:
        print(f"[ERROR] Failed to migrate {filename}: {str(e)}")
        return {
            "success": False,
            "chat_id": chat_id,
            "source": source,
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser(description="Migrate JSON sessions to SQLite")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be migrated without changing DB")
    args = parser.parse_args()

    # Find sessions directory
    project_root = Path(__file__).parent.parent
    sessions_dir = project_root / "data" / "sessions"

    if not sessions_dir.exists():
        print(f"Sessions directory not found: {sessions_dir}")
        return

    # Find all JSON files
    json_files = list(sessions_dir.glob("*.json"))

    if not json_files:
        print("No session files found to migrate")
        return

    print(f"Found {len(json_files)} session files")
    if args.dry_run:
        print("[DRY-RUN MODE] No changes will be made\n")
    else:
        print("[MIGRATION MODE] Writing to SQLite\n")

    # Migrate each file
    results = []
    for filepath in json_files:
        result = migrate_session(str(filepath), dry_run=args.dry_run)
        results.append(result)

    # Summary
    print("\n" + "="*60)
    print("MIGRATION SUMMARY")
    print("="*60)

    successful = sum(1 for r in results if r.get("success"))
    failed = len(results) - successful
    total_tasks = sum(r.get("tasks_migrated", 0) for r in results)
    skipped = sum(1 for r in results if r.get("skipped"))

    print(f"Total sessions: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Skipped (already migrated): {skipped}")
    print(f"Failed: {failed}")
    print(f"Total tasks migrated: {total_tasks}")

    if args.dry_run:
        print("\n[DRY-RUN] Run without --dry-run to apply changes")
    else:
        print("\n[COMPLETE] Migration finished")

    # Exit with error code if any failed
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
