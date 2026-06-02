"""Shared API-level state — worker loop ref and health metrics.

Separated from app.py to avoid circular imports between app factory and routes.
"""

from __future__ import annotations

import asyncio
from typing import Optional

_worker_loop_ref: Optional[asyncio.Task] = None

health_metrics: dict = {
    "startup_time": None,
    "last_success": None,
    "total_tasks": 0,
    "failed_tasks": 0,
    "errors_last_hour": [],
    "last_deployment_verification": {
        "timestamp": None,
        "healthy": None,
        "auto_rollback_count": 0,
    },
}
