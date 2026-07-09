"""Tiered commander queue assembly."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

from agent.commander.constants import QUEUE_SEVERITY
from agent.commander.sla import sla_status_for_age_hours, _parse_ts
from agent.db import (
    db_commander_list_tickets,
    db_list_calendar_entries,
    db_list_leads,
)

logger = logging.getLogger(__name__)


def _age_hours(created_at: Optional[str]) -> float:
    dt = _parse_ts(created_at)
    if not dt:
        return 0.0
    return (datetime.now(timezone.utc) - dt).total_seconds() / 3600.0


def _queue_item(
    *,
    item_id: str,
    queue_type: str,
    title: str,
    severity: str,
    created_at: str,
    payload: Optional[Dict] = None,
    escalation_reason: Optional[str] = None,
    source: str = "system",
    confidence: float = 0.85,
) -> Dict:
    age = _age_hours(created_at)
    sla = sla_status_for_age_hours(age, queue_type)
    return {
        "id": item_id,
        "queue_type": queue_type,
        "title": title,
        "severity": severity,
        "age_hours": round(age, 2),
        "sla_status": sla,
        "created_at": created_at,
        "payload": payload or {},
        "escalation_reason": escalation_reason or f"Pending {queue_type}",
        "source": source,
        "confidence": confidence,
        "available_actions": ["approve", "reject", "defer"],
    }


def build_queue(severity_filter: Optional[str] = None) -> List[Dict]:
    items: List[Dict] = []

    for ticket in db_commander_list_tickets(status="open", limit=20):
        qtype = "wp_ticket"
        items.append(
            _queue_item(
                item_id=f"ticket-{ticket['id']}",
                queue_type=qtype,
                title=ticket["title"],
                severity=QUEUE_SEVERITY[qtype],
                created_at=ticket["created_at"],
                payload={"ticket_id": ticket["id"], "description": ticket["description"]},
                source=ticket.get("source", "telegram"),
            )
        )

    for row in db_list_calendar_entries(status="pending_approval", limit=30):
        qtype = "fb_post_pending"
        items.append(
            _queue_item(
                item_id=f"cal-{row['entry_id']}",
                queue_type=qtype,
                title=row.get("title") or "FB post",
                severity=QUEUE_SEVERITY[qtype],
                created_at=row.get("updated_at") or row.get("created_at"),
                payload={
                    "entry_id": row["entry_id"],
                    "body_nl": row.get("body_nl"),
                    "platform": row.get("platform"),
                },
                source="calendar",
                confidence=0.9,
            )
        )

    for lead in db_list_leads(limit=10):
        score = lead.get("game_score") or 0
        if score >= 80:
            qtype = "hot_lead"
            items.append(
                _queue_item(
                    item_id=f"lead-{lead['id']}",
                    queue_type=qtype,
                    title=f"Hot lead: {lead.get('email', '')}",
                    severity=QUEUE_SEVERITY[qtype],
                    created_at=lead.get("created_at"),
                    payload=lead,
                    source="leads",
                    confidence=min(1.0, score / 100.0),
                )
            )

    order = {"CRITICAL": 0, "ACTION": 1, "INFO": 2}
    items.sort(key=lambda x: (order.get(x["severity"], 9), -x["age_hours"]))

    if severity_filter:
        items = [i for i in items if i["severity"] == severity_filter.upper()]

    return items


def build_priorities_today(max_items: int = 3) -> List[Dict]:
    queue = build_queue()
    critical = [q for q in queue if q["severity"] == "CRITICAL"]
    action = [q for q in queue if q["severity"] == "ACTION"]
    merged = critical + action
    return merged[:max_items]
