"""Event-Driven Core v1 — SQLite brain_events processor."""

from __future__ import annotations

import logging
from typing import Any, Dict

from agent.db import db_claim_brain_events, db_finish_brain_event

logger = logging.getLogger(__name__)


def process_brain_events(limit: int = 20, *, send_telegram: bool = True) -> Dict[str, Any]:
    """
    Idempotent consumer for pending brain_events.
    Side-effects for health/CEO live in brain_bus handlers.
    """
    claimed = db_claim_brain_events(limit=limit)
    done = 0
    dead = 0
    reactions: list = []
    for ev in claimed:
        eid = int(ev["id"])
        etype = ev.get("event_type") or ""
        payload = ev.get("payload") or {}
        corr = ev.get("correlation_id")
        source = ev.get("source_brain") or "mb"
        try:
            reaction = _dispatch_event(
                etype,
                payload,
                correlation_id=corr,
                source_brain=source,
                send_telegram=send_telegram,
            )
            if reaction:
                reactions.append({"event_id": eid, **reaction})
            logger.info(
                "[brain_events] processed id=%s type=%s corr=%s",
                eid,
                etype,
                corr,
            )
            db_finish_brain_event(eid, "done")
            done += 1
        except Exception as exc:
            logger.error("[brain_events] dead id=%s: %s", eid, exc)
            db_finish_brain_event(eid, "dead", error_message=str(exc))
            dead += 1
    return {
        "claimed": len(claimed),
        "done": done,
        "dead": dead,
        "reactions": reactions,
    }


def _dispatch_event(
    etype: str,
    payload: Dict[str, Any],
    *,
    correlation_id: Any,
    source_brain: str,
    send_telegram: bool,
) -> Dict[str, Any]:
    from agent.marketing import brain_bus

    if etype == "system.health.degraded":
        return brain_bus.handle_system_health_degraded(
            payload,
            correlation_id=correlation_id,
            source_brain=source_brain,
            send_telegram=send_telegram,
        )
    if etype == "system.health.recovered":
        return brain_bus.handle_system_health_recovered(
            payload,
            correlation_id=correlation_id,
        )
    if etype == "ceo.priority":
        return brain_bus.handle_ceo_priority(
            payload,
            correlation_id=correlation_id,
            source_brain=source_brain,
            send_telegram=send_telegram,
        )
    if etype in (
        "campaign.decision.proposed",
        "campaign.fact.updated",
        "hypothesis.review_due",
        "lead.spike",
    ):
        # v1 acknowledge — producers already persisted domain state
        return {"ok": True, "action": "ack"}
    logger.warning("[brain_events] unknown type=%s — ack", etype)
    return {"ok": True, "action": "ack_unknown"}
