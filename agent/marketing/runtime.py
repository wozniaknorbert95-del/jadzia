"""Marketing Brain runtime cycle — decision + Telegram shadow proposals + EDC."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def _touch_mb_heartbeat(success: bool, error: Optional[str] = None) -> None:
    from agent.db import db_commander_upsert_agent_state
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    db_commander_upsert_agent_state(
        "marketing_brain",
        {
            "status": "LIVE",
            "last_run_at": now,
            "last_error": None if success else (error or "error"),
            "expected_interval_seconds": 3600,
        },
    )


def run_marketing_brain_cycle(*, send_telegram: bool = True) -> Dict[str, Any]:
    """
    F1 cycle:
    1) decision_engine on DTL facts
    2) Telegram proposals for ACTION/CRITICAL (shadow)
    3) process brain_events
    """
    from agent.marketing.brain_events import process_brain_events
    from agent.marketing.decision_engine import run_decision_cycle
    from agent.marketing.telegram_proposals import send_mb_proposal_telegram

    try:
        cycle = run_decision_cycle()
        sent = 0
        if send_telegram:
            for rec in cycle.get("records") or []:
                decision = rec["decision"]
                if decision.severity in ("ACTION", "CRITICAL") or decision.heuristic_rule_id != "HEU_NO_SIGNAL":
                    if send_mb_proposal_telegram(
                        rec["action_id"],
                        decision,
                        rec.get("mb_mode") or "shadow",
                    ):
                        sent += 1
        events = process_brain_events(limit=50)
        _touch_mb_heartbeat(True)
        summary = {
            "ok": True,
            "mb_mode": cycle.get("mb_mode"),
            "records": len(cycle.get("records") or []),
            "telegram_sent": sent,
            "brain_events": events,
        }
        logger.info(
            "[mb.runtime] ok records=%s tg=%s events_done=%s",
            summary["records"],
            sent,
            events.get("done"),
        )
        return summary
    except Exception as exc:
        logger.error("[mb.runtime] failed: %s", exc, exc_info=True)
        _touch_mb_heartbeat(False, str(exc))
        return {"ok": False, "error": str(exc)}
