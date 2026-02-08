## CODE ANALYSIS

### How task gets into queue

1. **Telegram:** User sends `/zadanie` → [interfaces/telegram_api.py](interfaces/telegram_api.py) handles webhook, calls `create_task(instruction, chat_id, ...)` from [interfaces/telegram_worker_client.py](interfaces/telegram_worker_client.py) (HTTP POST to Worker API `/worker/task`). Telegram API does **not** call `add_task_to_queue` or any state.py function directly.

2. **Worker API:** [interfaces/api.py](interfaces/api.py) `worker_create_task` (lines 349–419) receives the request. It calls `load_state(chat_id, source)` and checks if there is an **active non-terminal** task:
   - **If yes:** it calls `add_task_to_queue(chat_id, task_id, request.instruction, source, ...)` from [agent/state.py](agent/state.py) (lines 569–615). That function, under lock, loads state, creates a minimal task entry in `state["tasks"][task_id]`, does `state.setdefault("task_queue", []).append(task_id)`, and `save_state(state, chat_id, source)`. So the task is appended to **sessions.task_queue** (and synced to SQLite `sessions.task_queue` via `_sync_to_sqlite`).
   - **If no** (no active task or active is COMPLETED/FAILED/ROLLED_BACK): it does **not** call `add_task_to_queue`. It calls `create_operation(...)` (state.py 694–744), which creates the task in `state["tasks"]`, sets `state["active_task_id"] = task_id`, and `state.setdefault("task_queue", [])` but **never** appends `task_id` to `task_queue`. Then it runs `process_message` in the same HTTP request.

**Function flow:** `telegram_api.py` → `create_task()` (HTTP) → `api.worker_create_task` → **only when there is already an active task:** `state.add_task_to_queue` → `save_state` → `_sync_to_sqlite` → `sessions.task_queue` (and `tasks` table). For the **first** task in a session, flow is: `worker_create_task` → `create_operation` → **no** `add_task_to_queue` → `process_message` in request.

---

### Why queue is empty

- **Root cause:** For the first task (or when the active task is done), `worker_create_task` does **not** call `add_task_to_queue`. It calls `create_operation`, which:
  - Writes the task to `state["tasks"]` and sets `state["active_task_id"]`;
  - Does **not** add the task to `state["task_queue"]` (it only does `state.setdefault("task_queue", [])`, so the list stays empty).
- **Persistence:** `save_state` → `_sync_to_sqlite` writes:
  - `state["task_queue"]` to **sessions.task_queue** (so it remains `[]`);
  - each `state["tasks"][task_id]` to the **tasks** table via `db_create_task` / `db_update_task`.
- So the **tasks** table has a row for the task, but **sessions.task_queue** is empty. The task is only in the queue when it was added via `add_task_to_queue` (i.e. when there was already an active task at create time).

---

### How worker loop loads the queue

- At [interfaces/api.py](interfaces/api.py) ~808: `queue = state.get("task_queue") or []`.
- `state` comes from `load_state(chat_id, source)` ([agent/state.py](agent/state.py) 314). `load_state` uses `_load_state_from_sqlite` (281–311), which:
  - Calls `db_get_session(chat_id, source)` → reads **sessions** row, including **sessions.task_queue** (JSON list);
  - Calls `db_get_tasks_for_session(chat_id, source)` → reads **tasks** table for that (chat_id, source);
  - Builds `state = { "tasks": {...}, "active_task_id": session["active_task_id"], "task_queue": session["task_queue"] }`.
- So the worker loop gets **task_queue** from **sessions.task_queue**, not from the **tasks** table. If the first task was created via `create_operation` only, `sessions.task_queue` is `[]`, so the loop sees an empty queue. Recovery (api.py 811–819) then uses `active_task_id` when queue is empty and the active task is non-terminal.

---

### Fix needed

- **No change required** for correct behaviour: the recovery logic in [interfaces/api.py](interfaces/api.py) lines 811–819 already handles “empty queue + active non-terminal task” by setting `next_task_id = active_id` and running `process_message`, so the first (or orphaned) task is picked up by the worker loop.
- **Optional consistency change:** If you want every active task to also appear in `task_queue` (so the queue is never “empty with an active task”), then in [agent/state.py](agent/state.py) inside `create_operation`, after `state["active_task_id"] = task_id`, add: `state.setdefault("task_queue", []).append(task_id)` before `save_state`. That would make the first task visible in the queue as well; the worker would then normally get it via `get_next_task_from_queue` when `active_id` is terminal, instead of only via the recovery path. Side effect: the same task would be both `active_task_id` and the first element of `task_queue` until it completes (then it’s popped). Current design avoids that by design (first task runs inline; only subsequent ones are queued).
