"""Webhook notifications — re-exports from interfaces.webhooks."""

from interfaces.webhooks import (
    set_health_metrics,
    record_task_success,
    record_task_failure,
    record_deployment_verification,
    notify_webhook,
)

__all__ = [
    "set_health_metrics",
    "record_task_success",
    "record_task_failure",
    "record_deployment_verification",
    "notify_webhook",
]
