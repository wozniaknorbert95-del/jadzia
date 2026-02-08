# Worker loop – root cause and fix

## Root cause (why the loop “didn’t process” Telegram queue)

1. **No visibility** – The loop had almost no logging. It was unclear whether:
   - Sessions were loaded (`db_list_all_sessions`)
   - State had a non-empty queue
   - `active_task_id` was set and whether its status was terminal
   - `get_next_task_from_queue` / `mark_task_completed` returned a task
   - `process_message` was ever started or failed

2. **One task per session at a time** – The loop only starts a new task when:
   - `active_task_id` is **None** → it calls `get_next_task_from_queue` and runs the next task, or
   - `active_task_id` is set and status is **terminal** (completed/failed/rolled_back) → it calls `mark_task_completed` (which sets the next task as active) and runs that next task.
   So if the current task is still in `planning` or `in_progress`, the queue is not advanced and the next task is not started. That is by design; without logs it looked like “the loop doesn’t process”.

3. **Exceptions could be silent** – `process_message` was started with `asyncio.create_task(...)` and no callback. Exceptions inside it did not show up in the loop logs.

4. **LockError** – If the session lock was held (e.g. another request or a long `process_message`), `get_next_task_from_queue` or `mark_task_completed` could raise `LockError`. The loop only printed a short message and continued; no traceback.

## Fix (code changes)

- **Logging**
  - Start/end of each iteration (with iteration number).
  - Sessions: count and list `(chat_id, source)`.
  - Per session: whether state is missing, queue length, `active_task_id`, task status.
  - When advancing: result of `mark_task_completed` or `get_next_task_from_queue` (`next_task_id`).
  - When starting work: `task_id`, `user_input` length, and that `process_message` is called with `push_to_telegram=True`.
  - When skipping: no state, empty queue, empty `user_input`, or “active task not terminal”.

- **Error handling**
  - `LockError`: catch explicitly and log “session busy”, then continue.
  - Other exceptions: full traceback (per session and per iteration).
  - `process_message` failures: `add_done_callback` on the created task to log and print traceback when the task raises.

- **Continuation** – Outer `try/except` keeps the loop running; on any exception it logs, then `await asyncio.sleep(interval)` and continues. No data loss; only logging and retry.

- **`push_to_telegram=True`** – Already passed in the only place the loop starts `process_message`; no change needed.

## Deployment

Restart the app so the new worker loop code and logging are loaded.

**Single command (from project root):**

```bash
# If you run with uvicorn (development or production)
uvicorn interfaces.api:app --host 0.0.0.0 --port 8000
```

If you use a process manager (systemd, Docker, etc.), restart that service instead so it runs the same command with the updated code.

**Env (optional):**

- `WORKER_LOOP_INTERVAL_SECONDS=15` (default) – interval between queue checks. Set to `0` to disable the worker loop.

## Expected log output after fix

**Loop disabled (interval 0):**

```
  [worker_loop] disabled (WORKER_LOOP_INTERVAL_SECONDS <= 0)
```

**Loop enabled, no sessions:**

```
  [worker_loop] iteration 1 start
  [worker_loop] no sessions found
  [worker_loop] iteration 1 end, sleeping 15s
```

**Loop enabled, one Telegram session with queued task and no active task:**

```
  [worker_loop] iteration 1 start
  [worker_loop] sessions count=1 list=[('telegram_123456', 'telegram')]
  [worker_loop] session telegram/telegram_123456: get_next_task_from_queue => next_task_id=abc-123
  [task_id=abc-123] get_next_task_from_queue chat_id=telegram_123456
  [worker_loop] session telegram/telegram_123456 task_id=abc-123: starting process_message (push_to_telegram=True) user_input_len=42
  [worker_loop] iteration 1 end, sleeping 15s
```

**Loop enabled, active task still running (queue waiting):**

```
  [worker_loop] session telegram/telegram_123456: active_id=task-1 status=planning queue_len=1
  [worker_loop] session telegram/telegram_123456: active task not terminal, waiting
```

**When process_message fails (e.g. API error):**

```
  [worker_loop] process_message failed chat_id=telegram_123456 source=telegram task_id=abc-123: ...
  Traceback (most recent call last):
  ...
```

After deployment, use these patterns to confirm that sessions are found, queue is seen, and either “waiting” or “starting process_message” appears, and that Telegram notifications are sent when the task reaches `plan_approval` (existing agent/telegram logging).
