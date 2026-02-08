# TELEGRAM FLOW DIAGNOSIS - Complete Report

### STAGE 1: Webhook Reception
Status: [ ] PASS / [x] FAIL (not run – SSH to VPS timed out from this environment)
Evidence: Commands must be run manually on VPS:
```bash
ssh root@185.243.54.115 'tail -200 /root/jadzia/logs/jadzia.log | grep -E "(POST /telegram/webhook|telegram_api)"'
```
Finding: Run the command on VPS to confirm webhook is hit and response status. Check for Telegram webhook log lines and any 4xx/5xx.

### STAGE 2: Task Creation
Status: [ ] PASS / [x] FAIL (not run – SSH to VPS timed out)
Evidence: Run on VPS (schema may use `user_input`; if query fails run `.schema tasks` first):
```bash
sqlite3 /root/jadzia/data/jadzia.db ".schema tasks"
sqlite3 /root/jadzia/data/jadzia.db "SELECT task_id, status, queue_position, created_at, instruction FROM tasks WHERE chat_id=\"telegram_6746343970\" AND source=\"telegram\" ORDER BY created_at DESC LIMIT 5;"
```
Finding: Confirm tasks exist in DB with status/position; if no rows, tasks are not being created or schema differs.

### STAGE 3: Worker Loop Pickup
Status: [ ] PASS / [x] FAIL (not run – SSH to VPS timed out)
Evidence: Run on VPS:
```bash
ssh root@185.243.54.115 'tail -200 /root/jadzia/logs/jadzia.log | grep -E "(telegram_6746343970|next_task_id|process_message)"'
```
Finding: If worker never logs session telegram/telegram_6746343970 or get_next_task_from_queue => next_task_id=, the loop is skipping this session (see Stage 6).

### STAGE 4: Process Message Execution
Status: [ ] PASS / [x] FAIL (not run – SSH to VPS timed out)
Evidence: Run on VPS:
```bash
ssh root@185.243.54.115 'tail -200 /root/jadzia/logs/jadzia.log | grep -E "(agent.py|planning|push_to_telegram)"'
```
Finding: If no planning/push logs for telegram session, process_message is not run for that chat_id/source.

### STAGE 5: Errors/Exceptions
Status: [ ] NO ERRORS / [ ] ERRORS FOUND (not run – SSH to VPS timed out)
Evidence: Run on VPS:
```bash
ssh root@185.243.54.115 'tail -100 /root/jadzia/logs/jadzia-error.log'
```
Finding: Check for Timeout, LockError, 5xx, or Telegram send errors.

### STAGE 6: Code Review - Queue Logic
Status: [x] CORRECT (bug was found; fix implemented) / [ ] BUG FOUND (unfixed)
Finding: The bug was in interfaces/api.py: the worker loop used to skip any session with empty `task_queue` (no recovery for orphaned active task). For the first Telegram task, `worker_create_task` calls `create_operation()` (sets `active_task_id`, does not add to `task_queue`) then runs `process_message` in the same request; if that request times out after create_operation, the session is left with active_task_id set and task_queue=[], so the loop skipped it forever. **The fix is implemented** in interfaces/api.py lines 811–819: when `task_queue` is empty, the loop now checks for `active_task_id` with non-terminal status and sets `next_task_id = active_id` (recovery path), then proceeds to run `process_message`. This recovers orphaned tasks after webhook timeout.

### STAGE 7: Code Review - Worker Client
Status: [x] CORRECT / [ ] BUG FOUND
Finding: interfaces/telegram_worker_client.py `create_task` sends correct payload (instruction, chat_id, test_mode). API derives source from chat_id (telegram_* → telegram). JWT and base URL from env; no bug found in client.

---

## ROOT CAUSE

The worker loop used to skip every session whose `task_queue` is empty. The first task in a new Telegram (or HTTP) session is created with `create_operation` and is not enqueued; it is run synchronously in the webhook request. If that request times out or fails after the session and task are written to the DB but before or during `process_message`, the session is left with an active non-terminal task and an empty queue. The worker loop then never considered such sessions, so the task was never picked up and Telegram tasks appeared "not processed." The fix (recovery path for empty queue + non-terminal active task) is now in place in api.py.

## PROPOSED FIX

**Files to modify:**
1. **interfaces/api.py** – In `_worker_loop`, when `task_queue` is empty, do not skip immediately; if the session has an `active_task_id` and that task's status is not terminal, set `next_task_id = active_id` (recovery path) and proceed to run `process_message`. This recovers orphaned tasks (e.g. after webhook timeout). Double execution is avoided because the same session is protected by `agent_lock`; if the webhook is still running it holds the lock and the worker gets `LockError` and skips.

**Implementation status:** This fix is already present in interfaces/api.py (lines 811–819).

**Why this fix:** Sessions with empty queue but non-terminal active task were ignored; they should be processed once so the task can complete or move to awaiting approval.

**Side effects:** Worker may run `process_message` for a task that was intended to run only in the webhook; lock ensures only one runner at a time. If a task is truly stuck (e.g. external hang), existing stale/awaiting-timeout logic still applies.

## VERIFICATION PLAN

After fix deployed on VPS:
1. Restart jadzia: `sudo systemctl restart jadzia`.
2. From Telegram send `/zadanie test` and wait for reply or approval buttons (or queue message).
3. If first task was orphaned before fix, trigger worker loop (wait up to `WORKER_LOOP_INTERVAL_SECONDS`) and check logs for `session telegram/telegram_6746343970` and `starting process_message` for that task_id.
4. Expected: Either webhook completes and user sees reply, or worker loop picks up the task within one interval and user gets reply/approval via push_to_telegram.
