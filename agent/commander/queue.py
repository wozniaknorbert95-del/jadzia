"""Tiered commander queue assembly."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

from agent.commander.constants import QUEUE_SEVERITY
from agent.commander.sla import freshness_status, sla_status_for_age_hours, _parse_ts
from agent.db import (
    db_commander_list_tickets,
    db_list_analytics_snapshots,
    db_list_calendar_entries,
    db_list_leads,
)
from agent.publishers.facebook import parse_publish_error

logger = logging.getLogger(__name__)

SEVERITY_POLICY_REF = "D0.8"


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
        "severity_policy_ref": SEVERITY_POLICY_REF,
    }


def build_queue(severity_filter: Optional[str] = None) -> List[Dict]:
    items: List[Dict] = []

    for ticket in db_commander_list_tickets(status="open", limit=20):
        ticket_source = ticket.get("source") or "telegram"
        if ticket_source == "brief_sales_cta":
            from agent.nodes.brief_node import parse_sales_cta_ticket_fields

            qtype = "sales_cta"
            fields = parse_sales_cta_ticket_fields(str(ticket.get("description") or ""))
            lead_id_raw = fields.get("lead_id")
            try:
                lead_id = int(lead_id_raw) if lead_id_raw else None
            except (TypeError, ValueError):
                lead_id = None
            payload = {
                "ticket_id": ticket["id"],
                "description": ticket["description"],
                "lead_id": lead_id,
                "id": lead_id,
                "cta_sku": fields.get("cta_sku"),
                "wizard_deeplink": fields.get("wizard_deeplink"),
            }
            item = _queue_item(
                item_id=f"ticket-{ticket['id']}",
                queue_type=qtype,
                title=ticket["title"],
                severity=QUEUE_SEVERITY[qtype],
                created_at=ticket["created_at"],
                payload=payload,
                source=ticket_source,
                escalation_reason="Sales CTA follow-up from weekly brief",
            )
            item["available_actions"] = ["acked", "snoozed", "closed", "defer"]
            items.append(item)
            continue

        qtype = "wp_ticket"
        items.append(
            _queue_item(
                item_id=f"ticket-{ticket['id']}",
                queue_type=qtype,
                title=ticket["title"],
                severity=QUEUE_SEVERITY[qtype],
                created_at=ticket["created_at"],
                payload={"ticket_id": ticket["id"], "description": ticket["description"]},
                source=ticket_source,
            )
        )

    for row in db_list_calendar_entries(status="failed", limit=30):
        pr_raw = row.get("publish_result")
        pr: dict = {}
        if pr_raw:
            try:
                pr = json.loads(pr_raw) if isinstance(pr_raw, str) else pr_raw
            except json.JSONDecodeError:
                pr = {}
        human = parse_publish_error(pr) if pr else "Publikacja nie powiodła się"
        qtype = "publish_failed"
        items.append(
            _queue_item(
                item_id=f"failed-{row['entry_id']}",
                queue_type=qtype,
                title=f"Publish failed: {row.get('title', 'post')}",
                severity=QUEUE_SEVERITY[qtype],
                created_at=row.get("updated_at") or row.get("created_at"),
                payload={
                    "entry_id": row["entry_id"],
                    "error_pl": human,
                    "content_type": row.get("content_type"),
                },
                source="calendar",
                escalation_reason=human,
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

    now = datetime.now(timezone.utc)
    for row in db_list_calendar_entries(status="approved", limit=50):
        sched_raw = row.get("scheduled_publish_at") or row.get("scheduled_at")
        if not sched_raw:
            continue
        try:
            sched_dt = datetime.fromisoformat(str(sched_raw).replace("Z", "+00:00"))
            if sched_dt.tzinfo is None:
                sched_dt = sched_dt.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            continue
        if sched_dt <= now:
            qtype = "scheduled_publish_due"
            items.append(
                _queue_item(
                    item_id=f"due-{row['entry_id']}",
                    queue_type=qtype,
                    title=f"Publish due: {row.get('title', 'post')}",
                    severity=QUEUE_SEVERITY[qtype],
                    created_at=sched_raw,
                    payload={"entry_id": row["entry_id"]},
                    source="calendar",
                    escalation_reason="Scheduled publish time passed",
                )
            )

    for lead in db_list_leads(limit=10):
        if lead.get("is_test") is True:
            continue
        disposition = (lead.get("disposition") or "open").lower()
        if disposition in ("closed", "snoozed"):
            continue
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

    from agent.commander.agents_registry import list_agents

    for agent in list_agents():
        if not agent.get("sla_ok") and agent.get("last_error"):
            qtype = "agent_error"
            items.append(
                _queue_item(
                    item_id=f"agent-{agent['agent_id']}",
                    queue_type=qtype,
                    title=f"Agent error: {agent['label']}",
                    severity=QUEUE_SEVERITY[qtype],
                    created_at=agent.get("last_run_at") or datetime.now(timezone.utc).isoformat(),
                    payload={"agent_id": agent["agent_id"], "error": agent.get("last_error")},
                    source="agents",
                    escalation_reason=agent.get("last_error") or "Agent silent",
                    confidence=0.5,
                )
            )

    snap_rows = db_list_analytics_snapshots(limit=1)
    ga4_at = snap_rows[0].get("generated_at") if snap_rows else None
    ga4_fresh = freshness_status("ga4", ga4_at)
    if ga4_fresh["status"] in ("amber", "red"):
        qtype = "analytics_stale"
        items.append(
            _queue_item(
                item_id="analytics-stale-ga4",
                queue_type=qtype,
                title="Analytics stale: GA4",
                severity=QUEUE_SEVERITY[qtype],
                created_at=ga4_at or datetime.now(timezone.utc).isoformat(),
                payload=ga4_fresh,
                source="analytics",
                escalation_reason=f"GA4 freshness {ga4_fresh['status']}",
            )
        )

    brief_setting = None
    try:
        from agent.db import db_commander_get_setting

        brief_setting = db_commander_get_setting("weekly_brief:last_sent")
    except Exception:
        pass
    if brief_setting:
        try:
            sent_at = json.loads(brief_setting["value_json"])
            qtype = "weekly_brief_ready"
            items.append(
                _queue_item(
                    item_id="weekly-brief",
                    queue_type=qtype,
                    title="Weekly brief ready",
                    severity=QUEUE_SEVERITY[qtype],
                    created_at=sent_at,
                    source="brief",
                )
            )
        except json.JSONDecodeError:
            pass

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
