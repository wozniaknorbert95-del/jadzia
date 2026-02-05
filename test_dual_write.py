# Test script: test_dual_write.py
from agent.state import create_operation, load_state
from agent.db import db_get_session, db_get_task
import uuid

# Create test task
chat_id = "dual_write_test"
source = "http"
task_id = str(uuid.uuid4())

# Create via state.py (writes to JSON + SQLite)
create_operation(
    chat_id=chat_id,
    source=source,
    task_id=task_id,
    user_input="Test dual write",
    dry_run=False
)

# Verify JSON
state = load_state(chat_id, source)
print(f"JSON has task: {task_id in state.get('tasks', {})}")

# Verify SQLite
session = db_get_session(chat_id, source)
print(f"SQLite has session: {session is not None}")

task = db_get_task(task_id)
print(f"SQLite has task: {task is not None}")

if task:
    print(f"Task status in SQLite: {task['status']}")

print("\nDual-write test complete!")
