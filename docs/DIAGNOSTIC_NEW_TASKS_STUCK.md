# Full diagnostic: WHY new tasks stuck (sessions table not updated)

## Commands run from this environment

- **1 & 2 (SQLite):** Failed due to PowerShell quoting; run manually on VPS (see below).
- **3 (grep):** Succeeded. Logs show:
  - `find_task_by_id: found in session telegram_telegram_6746343970` (i.e. source=`telegram`, chat_id=`telegram_6746343970`).
  - Worker loop lists session `('telegram_6746343970', 'telegram')` among 26 sessions.

So the worker **does** see the telegram session and **can** find a task in it. That implies at least one task was written to the DB (tasks table + session state) at some point.

---

## Code path: when does the sessions table get updated?

1. **Telegram** → webhook → [interfaces/telegram_api.py](interfaces/telegram_api.py) → `chat_id = get_jadzia_chat_id(request.user_id)` (= `telegram_6746343970`) → `create_task(instruction, chat_id, ...)` (HTTP POST to Worker API `/worker/task`).

2. **Worker API** [interfaces/api.py](interfaces/api.py) `worker_create_task`:
   - Receives `request.chat_id` (= `telegram_6746343970`), sets `source = "telegram"`.
   - If there is an **active non-terminal** task → calls `add_task_to_queue(...)` → `save_state` → **sessions** get `task_queue` updated (and **tasks** get new row).
   - If there is **no** active task (or it’s done) → calls **`create_operation(...)`** (no queue), then `process_message(...)`.
     - **`create_operation`** [agent/state.py](agent/state.py) 694–744: under lock, `load_state(chat_id, source)`, then `state["tasks"][task_id] = ...`, `state["active_task_id"] = task_id`, `state.setdefault("task_queue", [])` (stays `[]`), then **`save_state(state, chat_id, source)`**.

3. **`save_state`** → **`_sync_to_sqlite(chat_id, source, state)`** [agent/state.py](agent/state.py) 68–134:
   - `db_create_or_update_session(chat_id, source)` – ensure session row exists.
   - `db_set_active_task(chat_id, source, state["active_task_id"])` – **writes `active_task_id` to sessions**.
   - `db_update_task_queue(chat_id, source, state["task_queue"])` – **writes `task_queue` to sessions**.
   - Then syncs each task to **tasks** (create or update).

So **every** new task created via Worker API (either queued or “first” path) goes through `save_state` → `_sync_to_sqlite`, which **does** update the **sessions** row (`active_task_id`, `task_queue`). There is no code path that only inserts into **tasks** and skips sessions.

---

## Root cause hypotheses (why new tasks might “not be in session state”)

### A. Request never reaches Worker API (create_task never completes successfully)

- Telegram webhook runs (e.g. on n8n or another host) and calls `TELEGRAM_BOT_API_BASE_URL/worker/task`.
- If that URL is wrong, or JWT is invalid/expired, or request times out → HTTP 4xx/5xx or timeout → **no** `worker_create_task` run → **no** `create_operation` → **no** update to sessions or tasks for that request.
- **Check:** On VPS, logs for `POST /worker/task` and `worker_create_task chat_id=telegram_6746343970`. If there are no such lines when the user sends a new /zadanie, the request is not reaching the Worker API (or not with that chat_id).

### B. Request fails before or inside create_operation

- E.g. **LockError** (503) if the session is locked by another request/worker.
- Or exception inside `create_operation` (e.g. `load_state` fails, or `save_state` raises).
- Then the client gets 5xx/503 and **sessions** are not updated for that attempt.
- **Check:** jadzia.log and jadzia-error.log for 503, LockError, or tracebacks around the time of the new task.

### C. Two processes or two DB files

- If the Telegram webhook is handled by a **different** process (e.g. different app or another Jadzia instance) that uses a **different** DB path, then:
  - That process would update **its** `sessions`/`tasks`.
  - The VPS DB at `/root/jadzia/data/jadzia.db` would not see those updates.
- **Check:** Ensure only one Jadzia app runs and that it uses `data/jadzia.db` (or the same path you query). No second process writing to a different file.

### D. Session row overwritten after create_operation

- Theoretically, something could **load** an older state (e.g. without the new task) and **save** it later, overwriting `active_task_id` / `task_queue` in **sessions**.
- In the current code, the only writers for a given `(chat_id, source)` are the request that holds `agent_lock` and the worker loop when it runs for that session. Worker only calls `mark_task_completed` / `get_next_task_from_queue` when it decides to advance the queue; it doesn’t “clear” session without one of those. So overwrite would require a bug (e.g. wrong chat_id/source) or a second process (see C).
- **Check:** If **tasks** has the newest task but **sessions** has `active_task_id` NULL or an old task_id, then something is updating the session row after the fact; look for other code paths or processes that write to **sessions** for this chat_id/source.

---

## Why create_task “doesn’t update” sessions – summary

- In code, **create_task** (HTTP) → **worker_create_task** → **create_operation** → **save_state** → **\_sync_to_sqlite** always updates **sessions** (and **tasks**). So “create_task doesn’t update sessions” is not by design; it means one of:
  - The **HTTP create_task** call never succeeds (A), or
  - The handler **fails** before/during **create_operation** (B), or
  - Updates go to **another DB/process** (C), or
  - Session row is **overwritten** later (D).

---

## Commands to run on VPS (manual)

Run these **on the VPS** (e.g. after `ssh -i ~/.ssh/cyberfolks_key root@185.243.54.115`) to confirm state:

```bash
# 1. Newest task for telegram session
sqlite3 /root/jadzia/data/jadzia.db "SELECT task_id, status, created_at FROM tasks WHERE chat_id='telegram_6746343970' AND source='telegram' ORDER BY created_at DESC LIMIT 1;"

# 2. Session state (active_task_id, task_queue)
sqlite3 /root/jadzia/data/jadzia.db "SELECT active_task_id, task_queue FROM sessions WHERE chat_id='telegram_6746343970' AND source='telegram';"

# 3. Worker loop lines for this chat
tail -100 /root/jadzia/logs/jadzia.log | grep telegram_6746343970
```

**Interpretation:**

- If **tasks** has a new row but **sessions** has `active_task_id` NULL and `task_queue` = `[]` → something is wrong with session update (e.g. D or partial write).
- If **tasks** has **no** new row for the latest /zadanie → request never reached Worker API or failed before **create_operation** (A or B). Check logs for POST /worker/task and errors.
- If both **tasks** and **sessions** have the new task (active_task_id set) but the task still doesn’t progress → the problem is elsewhere (e.g. worker loop logic, timeout, or negative age_minutes), not “create_task doesn’t update sessions.”

---

## Fix needed (depends on diagnostic)

- **If A:** Fix URL/JWT/timeout so Telegram webhook’s `create_task` call reaches Worker API and returns 200.
- **If B:** Fix lock timeout or the failing step (e.g. DB error) so `create_operation` + `save_state` complete.
- **If C:** Use a single process and single DB path for all Telegram and worker traffic.
- **If D:** Track down the code or process that writes to **sessions** for this (chat_id, source) and fix overwrite.

No code change is suggested here until the VPS SQL results and logs confirm which of A–D applies.
