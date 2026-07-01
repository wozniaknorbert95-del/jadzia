"""FastAPI application factory with route registration and DI wiring."""

from __future__ import annotations

import asyncio
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api._state import health_metrics

load_dotenv()

_log = logging.getLogger("api.app")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="JADZIA API",
        description="AI Agent for online store management",
        version="1.0.0",
    )

    # ── CORS ──
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://flexgrafik.nl",
            "https://www.flexgrafik.nl",
            "https://app.flexgrafik.nl",
            "https://zzpackage.flexgrafik.nl",
            "https://api.zzpackage.flexgrafik.nl",
            "http://localhost:3000",
            "http://localhost:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Register routers ──
    from api.routes.chat import router as chat_router
    from api.routes.portal_qualify import router as portal_qualify_router
    from api.routes.leads import router as leads_router
    from api.routes.analytics import router as analytics_router
    from api.routes.content_calendar import router as content_calendar_router
    from api.routes.webhooks import router as inbound_webhooks_router
    from api.routes.health import router as health_router
    from api.routes.worker import router as worker_router
    from api.routes.dashboard import router as dashboard_router
    from api.routes.costs import router as costs_router
    from api.routes.sessions import router as sessions_router

    app.include_router(chat_router)
    app.include_router(portal_qualify_router)
    app.include_router(leads_router)
    app.include_router(analytics_router)
    app.include_router(content_calendar_router)
    app.include_router(inbound_webhooks_router)
    app.include_router(health_router)
    app.include_router(worker_router)
    app.include_router(dashboard_router)
    app.include_router(costs_router)
    app.include_router(sessions_router)

    # Telegram router (conditionally included)
    if os.getenv("TELEGRAM_BOT_ENABLED", "") == "1":
        try:
            from api.telegram import router as telegram_router
            app.include_router(telegram_router)
        except Exception as e:
            _log.warning("Failed to load Telegram router: %s", e)

    # ── Startup / shutdown ──
    @app.on_event("startup")
    async def on_startup():
        import api._state as _api_state
        from agent.state import cleanup_old_sessions

        Path("logs").mkdir(exist_ok=True)
        health_metrics["startup_time"] = datetime.now(timezone.utc).isoformat()

        # Clean up old sessions
        try:
            cleanup_old_sessions(days=7)
        except Exception as e:
            _log.warning("Session cleanup failed: %s", e)

        # Start worker loop
        try:
            _api_state._worker_loop_ref = asyncio.create_task(
                _worker_loop(), name="worker_loop"
            )
        except Exception as e:
            _log.error("Failed to start worker loop: %s", e)

    @app.on_event("shutdown")
    async def on_shutdown():
        import api._state as _api_state
        if _api_state._worker_loop_ref and not _api_state._worker_loop_ref.done():
            _api_state._worker_loop_ref.cancel()
            try:
                await _api_state._worker_loop_ref
            except asyncio.CancelledError:
                pass

    return app


# ──────────────────────────────────────────────
# Worker loop (background queue processor)
# ──────────────────────────────────────────────

TERMINAL_STATUSES = ("completed", "failed", "rolled_back")

WORKER_TASK_TIMEOUT_SECONDS = int(os.getenv("WORKER_TASK_TIMEOUT_SECONDS", "600") or "600")
WORKER_STALE_TASK_MINUTES = int(os.getenv("WORKER_STALE_TASK_MINUTES", "15") or "15")
WORKER_AWAITING_TIMEOUT_MINUTES = int(os.getenv("WORKER_AWAITING_TIMEOUT_MINUTES", "1440") or "1440")

_last_fb_publish_check: float = 0.0


async def _maybe_run_scheduled_fb_publish() -> None:
    """Publish approved Facebook entries when scheduled time is due (INT-011)."""
    global _last_fb_publish_check

    interval = int(os.getenv("FB_PUBLISH_CHECK_INTERVAL_SECONDS", "60") or "0")
    if interval <= 0:
        return

    now = time.monotonic()
    if now - _last_fb_publish_check < interval:
        return
    _last_fb_publish_check = now

    def _run() -> None:
        from agent.nodes.content_calendar_node import publish_due_scheduled_entries

        publish_due_scheduled_entries()

    try:
        await asyncio.to_thread(_run)
    except Exception as e:
        _log.error("[worker_loop] scheduled FB publish failed: %s", e)


async def _worker_loop():
    """Background loop: advance queues, run next task via process_message."""
    base_interval = int(os.getenv("WORKER_LOOP_INTERVAL_SECONDS", "15") or "0")
    if base_interval <= 0:
        _log.info("[worker_loop] disabled (WORKER_LOOP_INTERVAL_SECONDS <= 0)")
        return
    busy_sleep = int(os.getenv("WORKER_LOOP_BUSY_SLEEP_SECONDS", "2") or "2")
    max_idle_sleep = 30
    idle_backoff_sec = min(base_interval, max_idle_sleep)
    iter_num = 0

    while True:
        iter_num += 1
        had_work = False
        try:
            from agent.db import db_list_all_sessions, db_get_task
            from agent.state import (
                load_state,
                is_locked,
                get_current_status,
                update_operation_status,
                mark_task_completed,
                clear_active_task_and_advance,
                get_next_task_from_queue,
                OperationStatus,
                find_task_by_id,
            )
            from core.agent import process_message

            _log.debug("[worker_loop] iteration %s start", iter_num)
            try:
                sessions = await asyncio.to_thread(db_list_all_sessions)
            except Exception as e:
                _log.error("[worker_loop] db_list_all_sessions failed: %s", e)
                await asyncio.sleep(idle_backoff_sec)
                continue

            states = await asyncio.gather(
                *[asyncio.to_thread(load_state, c, s) for (c, s) in sessions]
            )

            for ((chat_id, source), state) in zip(sessions, states):
                try:
                    if not state:
                        continue
                    queue = state.get("task_queue") or []
                    active_id = state.get("active_task_id")
                    next_task_id = None

                    if not queue:
                        task = (state.get("tasks") or {}).get(active_id) if active_id else None
                        status = (task or {}).get("status") if task else None

                        if active_id and task is None:
                            row = db_get_task(active_id)
                            if row and row.get("chat_id") == chat_id and row.get("source") == source:
                                continue
                            try:
                                await asyncio.to_thread(clear_active_task_and_advance, chat_id, source)
                                had_work = True
                            except Exception as e:
                                _log.error("[worker_loop] failed to clear ghost: %s", e)
                            continue

                        if active_id and status == "queued":
                            next_task_id = active_id
                        elif active_id and status and status in TERMINAL_STATUSES:
                            next_task_id = await asyncio.to_thread(
                                mark_task_completed, chat_id, active_id, source
                            )
                        else:
                            continue
                    elif active_id:
                        task = (state.get("tasks") or {}).get(active_id)
                        status = (task or {}).get("status") if task else None

                        if task is None:
                            row = db_get_task(active_id)
                            if row and row.get("chat_id") == chat_id and row.get("source") == source:
                                continue
                            try:
                                next_task_id = await asyncio.to_thread(
                                    clear_active_task_and_advance, chat_id, source
                                )
                                had_work = True
                            except Exception as e:
                                _log.error("[worker_loop] failed to clear ghost: %s", e)
                                continue
                        elif status in TERMINAL_STATUSES:
                            next_task_id = await asyncio.to_thread(
                                mark_task_completed, chat_id, active_id, source
                            )
                        else:
                            if status == "queued":
                                next_task_id = active_id
                            elif await asyncio.to_thread(is_locked, chat_id, source):
                                continue
                            else:
                                if status == "planning" and task.get("awaiting_response", False):
                                    ts_str = (task.get("created_at") or "").strip()
                                    if ts_str and WORKER_AWAITING_TIMEOUT_MINUTES > 0:
                                        dt = _parse_timestamp_to_utc(ts_str)
                                        if dt:
                                            age_min = _safe_age_minutes(dt)
                                            if age_min > WORKER_AWAITING_TIMEOUT_MINUTES:
                                                await asyncio.to_thread(
                                                    update_operation_status,
                                                    OperationStatus.FAILED,
                                                    chat_id, source, task_id=active_id,
                                                )
                                                await asyncio.to_thread(
                                                    mark_task_completed, chat_id, active_id, source
                                                )
                                                next_task_id = active_id

                                if next_task_id is None:
                                    stale_min = WORKER_STALE_TASK_MINUTES
                                    ts_str = (task.get("updated_at") or "").strip()
                                    dt = _parse_timestamp_to_utc(ts_str) if ts_str else None
                                    if dt and stale_min > 0:
                                        age_min = _safe_age_minutes(dt)
                                        if age_min > stale_min:
                                            await asyncio.to_thread(
                                                update_operation_status,
                                                OperationStatus.FAILED,
                                                chat_id, source, task_id=active_id,
                                            )
                                            await asyncio.to_thread(
                                                mark_task_completed, chat_id, active_id, source
                                            )
                                            next_task_id = active_id
                    else:
                        next_task_id = await asyncio.to_thread(
                            get_next_task_from_queue, chat_id, source
                        )

                    if next_task_id:
                        task_payload = find_task_by_id(chat_id, next_task_id, source) or {}
                        user_input = task_payload.get("user_input", "")
                        dry_run = bool(task_payload.get("dry_run", False))
                        test_mode = bool(task_payload.get("test_mode", False))
                        webhook_url = task_payload.get("webhook_url")

                        try:
                            result = await asyncio.wait_for(
                                process_message(
                                    user_input,
                                    chat_id=chat_id,
                                    source=source,
                                    task_id=next_task_id,
                                    dry_run=dry_run,
                                    webhook_url=webhook_url,
                                    test_mode=test_mode,
                                    push_to_telegram=True,
                                    auto_advance=False,
                                ),
                                timeout=float(WORKER_TASK_TIMEOUT_SECONDS),
                            )

                            response_text, awaiting_input, input_type = result
                            if not awaiting_input:
                                try:
                                    current = await asyncio.to_thread(
                                        get_current_status, chat_id, source, next_task_id
                                    )
                                    if current and current in TERMINAL_STATUSES:
                                        await asyncio.to_thread(
                                            mark_task_completed, chat_id, next_task_id, source
                                        )
                                    else:
                                        await asyncio.to_thread(
                                            update_operation_status,
                                            OperationStatus.COMPLETED,
                                            chat_id, source, task_id=next_task_id,
                                        )
                                        await asyncio.to_thread(
                                            mark_task_completed, chat_id, next_task_id, source
                                        )
                                except Exception as e:
                                    _log.error("[worker_loop] failed to mark task completed: %s", e)
                        except asyncio.TimeoutError:
                            _log.info("[worker_loop] task %s timed out", next_task_id)
                            try:
                                await asyncio.to_thread(
                                    update_operation_status,
                                    OperationStatus.FAILED,
                                    chat_id, source, task_id=next_task_id,
                                )
                                await asyncio.to_thread(
                                    mark_task_completed, chat_id, next_task_id, source
                                )
                            except Exception as e:
                                _log.error("[worker_loop] failed to mark timeout: %s", e)
                        except asyncio.CancelledError:
                            _log.info("[worker_loop] task %s cancelled", next_task_id)
                            try:
                                await asyncio.to_thread(
                                    update_operation_status,
                                    OperationStatus.FAILED,
                                    chat_id, source, task_id=next_task_id,
                                )
                                await asyncio.to_thread(
                                    mark_task_completed, chat_id, next_task_id, source
                                )
                            except Exception:
                                pass
                            raise
                        else:
                            had_work = True
                except Exception as e:
                    _log.error("[worker_loop] session error %s/%s: %s", source, chat_id, e)

            await _maybe_run_scheduled_fb_publish()
            await asyncio.sleep(busy_sleep if had_work else idle_backoff_sec)
        except asyncio.CancelledError:
            _log.info("[worker_loop] cancelled")
            raise
        except Exception as e:
            _log.error("[worker_loop] unexpected error: %s", e, exc_info=True)
            await asyncio.sleep(idle_backoff_sec)


def _parse_timestamp_to_utc(ts_str: str) -> Optional[datetime]:
    """Parse ISO timestamp to UTC datetime."""
    if not ts_str or not ts_str.strip():
        return None
    try:
        dt = datetime.fromisoformat(ts_str.strip().replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.astimezone(timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt
    except (ValueError, TypeError) as e:
        _log.warning("_parse_timestamp_to_utc failed for %r: %s", ts_str, e)
        return None


def _safe_age_minutes(dt_utc: datetime) -> float:
    """Calculate age in minutes, clamped to 0."""
    age = datetime.now(timezone.utc) - dt_utc
    if age.total_seconds() < 0:
        return 0.0
    return age.total_seconds() / 60.0
