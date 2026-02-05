"""
Webhook notifications and health metrics callbacks.
Lives in interfaces to avoid circular imports (agent/approval -> api).
"""

import httpx
from datetime import datetime, timezone
from typing import Optional

from agent.log import log_event, log_error

# Set by api.py at startup so we can update metrics without importing api
_health_metrics: Optional[dict] = None


def set_health_metrics(metrics: dict) -> None:
    """Register the health metrics dict from api.py at startup."""
    global _health_metrics
    _health_metrics = metrics


def record_task_success() -> None:
    """Update health metrics on task completion."""
    if _health_metrics is not None:
        _health_metrics["last_success"] = datetime.now(timezone.utc).isoformat()
        _health_metrics["total_tasks"] = _health_metrics.get("total_tasks", 0) + 1


def record_task_failure(error: str) -> None:
    """Update health metrics on task failure."""
    if _health_metrics is not None:
        _health_metrics["failed_tasks"] = _health_metrics.get("failed_tasks", 0) + 1
        _health_metrics.setdefault("errors_last_hour", []).append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": error,
        })


def record_deployment_verification(
    timestamp_iso: str,
    healthy: bool,
    auto_rollback_triggered: bool = False,
) -> None:
    """Update health metrics with last deployment verification (self-healing)."""
    if _health_metrics is not None:
        verification = _health_metrics.setdefault(
            "last_deployment_verification",
            {"timestamp": None, "healthy": None, "auto_rollback_count": 0},
        )
        verification["timestamp"] = timestamp_iso
        verification["healthy"] = healthy
        if auto_rollback_triggered:
            verification["auto_rollback_count"] = verification.get("auto_rollback_count", 0) + 1


async def notify_webhook(
    webhook_url: str,
    task_id: str,
    status: str,
    result: dict,
) -> None:
    """Send webhook notification when task completes or fails. Does not raise."""
    if not webhook_url:
        return

    payload = {
        "task_id": task_id,
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "result": result,
    }

    if status == "completed":
        record_task_success()
    try:
        log_event(
            "webhook",
            f"[WEBHOOK] Calling {webhook_url}",
            task_id=task_id,
        )
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(webhook_url, json=payload)
            response.raise_for_status()
        log_event(
            "webhook",
            f"[WEBHOOK] Success: {response.status_code}",
            task_id=task_id,
        )
    except Exception as e:
        log_error(
            f"[WEBHOOK] Failed to notify {webhook_url}: {str(e)}",
            task_id=task_id,
        )
