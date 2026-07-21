"""Webhook notifications and health metrics callbacks."""

from datetime import UTC, datetime

import httpx

from agent.log import log_error, log_event
from core.webhook_url_guard import CallbackUrlError, redact_callback_url, validate_callback_url

_health_metrics: dict | None = None


def set_health_metrics(metrics: dict) -> None:
    global _health_metrics
    _health_metrics = metrics


def record_task_success() -> None:
    if _health_metrics is not None:
        _health_metrics["last_success"] = datetime.now(UTC).isoformat()
        _health_metrics["total_tasks"] = _health_metrics.get("total_tasks", 0) + 1


def record_task_failure(error: str) -> None:
    if _health_metrics is not None:
        _health_metrics["failed_tasks"] = _health_metrics.get("failed_tasks", 0) + 1
        _health_metrics.setdefault("errors_last_hour", []).append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "error": error,
            }
        )


def record_deployment_verification(
    timestamp_iso: str,
    healthy: bool,
    auto_rollback_triggered: bool = False,
) -> None:
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
    if not webhook_url:
        return
    try:
        validated_url = validate_callback_url(webhook_url)
    except CallbackUrlError as exc:
        log_error(
            f"[WEBHOOK] Rejected callback: {type(exc).__name__}",
            task_id=task_id,
        )
        return
    if validated_url is None:
        return
    callback_target = redact_callback_url(validated_url)

    payload = {
        "task_id": task_id,
        "status": status,
        "timestamp": datetime.now(UTC).isoformat(),
        "result": result,
    }

    if status == "completed":
        record_task_success()
    try:
        log_event("webhook", f"[WEBHOOK] Calling {callback_target}", task_id=task_id)
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client:
            response = await client.post(validated_url, json=payload)
            if response.is_redirect:
                log_error(
                    f"[WEBHOOK] Rejected redirect from {callback_target}",
                    task_id=task_id,
                )
                return
            response.raise_for_status()
        log_event("webhook", f"[WEBHOOK] Success: {response.status_code}", task_id=task_id)
    except Exception as exc:
        log_error(
            f"[WEBHOOK] Failed to notify {callback_target}: {type(exc).__name__}",
            task_id=task_id,
        )


__all__ = [
    "set_health_metrics",
    "record_task_success",
    "record_task_failure",
    "record_deployment_verification",
    "notify_webhook",
]
