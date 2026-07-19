"""Event-Driven Core v1 — SQLite brain_events processor."""

from __future__ import annotations

import logging
from typing import Any, Dict

from agent.db import db_claim_brain_events, db_finish_brain_event

logger = logging.getLogger(__name__)


def process_brain_events(limit: int = 20) -> Dict[str, Any]:
    """
    Idempotent consumer for pending brain_events.
    campaign.decision.proposed → already persisted; mark done.
    Future: lead.spike, system.health.degraded, hypothesis.review_due.
    """
    claimed = db_claim_brain_events(limit=limit)
    done = 0
    dead = 0
    for ev in claimed:
        eid = int(ev["id"])
        etype = ev.get("event_type") or ""
        try:
            if etype in (
                "campaign.decision.proposed",
                "campaign.fact.updated",
                "hypothesis.review_due",
                "system.health.degraded",
                "lead.spike",
            ):
                # v1: acknowledge + log; side-effects live in runtime/telegram
                logger.info(
                    "[brain_events] processed id=%s type=%s corr=%s",
                    eid,
                    etype,
                    ev.get("correlation_id"),
                )
                db_finish_brain_event(eid, "done")
                done += 1
            else:
                logger.warning("[brain_events] unknown type=%s id=%s", etype, eid)
                db_finish_brain_event(eid, "done")
                done += 1
        except Exception as exc:
            logger.error("[brain_events] dead id=%s: %s", eid, exc)
            db_finish_brain_event(eid, "dead", error_message=str(exc))
            dead += 1
    return {"claimed": len(claimed), "done": done, "dead": dead}
