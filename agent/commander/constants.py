"""Severity, SLA and risk tier constants."""

from __future__ import annotations

from typing import Dict, Tuple

Severity = str  # CRITICAL | ACTION | INFO

QUEUE_SEVERITY: Dict[str, Severity] = {
    "hot_lead": "CRITICAL",
    "agent_error": "CRITICAL",
    "wp_ticket": "CRITICAL",
    "publish_failed": "CRITICAL",
    "fb_post_pending": "ACTION",
    "scheduled_publish_due": "ACTION",
    "sales_cta": "ACTION",
    "cs_followup": "ACTION",
    "weekly_brief_ready": "INFO",
    "analytics_stale": "ACTION",
}

QUEUE_SLA_HOURS: Dict[str, float] = {
    "hot_lead": 4,
    "agent_error": 2,
    "wp_ticket": 8,
    "publish_failed": 2,
    "fb_post_pending": 24,
    "scheduled_publish_due": 1,
    "sales_cta": 4,
    "cs_followup": 48,
    "weekly_brief_ready": 48,
}

FRESHNESS_SLA_SECONDS: Dict[str, Tuple[int, int]] = {
    "ga4": (30 * 60, 2 * 3600),
    "orders": (15 * 60, 3600),
    "leads": (15 * 60, 3600),
    "worker": (2 * 60, 5 * 60),
    # DTL extras reuse ga4 SLA via report mapping; explicit keys for future
    "l0_pixel": (2 * 3600, 6 * 3600),
    "attribution": (30 * 60, 2 * 3600),
    "margin": (30 * 60, 2 * 3600),
}

ROLE_SCOPES: Dict[str, list[str]] = {
    "dowodca": ["*"],
    "delegat": [
        "marketing:approve",
        "marketing:publish",
        "marketing:unpublish",
        "queue:act",
        "leads:act",
        "commander:read",
    ],
    "viewer": ["*:read", "commander:read"],
}

BULK_APPROVE_LIMIT = 5
DAILY_ACTION_BUDGET_DEFAULT = 200

GRADUATION_DEFAULTS = {
    "min_approvals": 20,
    "max_override_rate_pct": 5.0,
    "min_confidence_avg": 0.7,
}
