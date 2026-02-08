# Verification: recovery logic vs empty queue

## Question

Is the recovery logic (811-819) placed **after** `if not queue: continue`? If yes, recovery would never run for an empty queue.

## Exact code (lines 808-820)

```python
 808|                    queue = state.get("task_queue") or []
 809|                    active_id = state.get("active_task_id")
 810|                    next_task_id = None
 811|                    if not queue:
 812|                        # Recovery: session has active task but empty queue (e.g. webhook timed out after create_operation)
 813|                        task = (state.get("tasks") or {}).get(active_id) if active_id else None
 814|                        status = (task or {}).get("status") if task else None
 815|                        if active_id and status and status not in TERMINAL_STATUSES:
 816|                            next_task_id = active_id
 817|                            print(f"  [worker_loop] session {source}/{chat_id}: recovery run for active_id={active_id} (empty queue)")
 818|                        else:
 819|                            continue
 820|                    elif active_id:
```

## Result: no conflict

- There is **no** `if not queue: continue` before the recovery block.
- Flow when `queue` is empty:
  1. Line 811: `if not queue:` → we **enter** the block (we do not `continue` here).
  2. Lines 812–816: recovery runs: if `active_id` and non-terminal `status`, we set `next_task_id = active_id`.
  3. Line 818–819: `else: continue` runs **only** when we are in the empty-queue branch **and** recovery conditions are not met (no `active_id`, or terminal status). Then we skip the session.

So recovery **does** run for an empty queue when there is an active non-terminal task. The only `continue` is in the `else` of the recovery check (empty queue but nothing to recover).

## Where a conflict would be

A conflict would look like this (this is **not** in the current code):

```python
if not queue:
    continue   # <-- this would make recovery unreachable
# Recovery: ...
```

Current code correctly has recovery **inside** `if not queue:` with `continue` only in the branch where recovery does not apply.
