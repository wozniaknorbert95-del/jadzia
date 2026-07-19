"""Brain Bus v1 — structured events VCMS/KODA/CEO → Marketing Brain."""

from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from agent.db import (
    db_commander_create_ticket,
    db_deactivate_quality_flags,
    db_enqueue_brain_event,
    db_insert_quality_flag,
)

logger = logging.getLogger(__name__)

ALLOWED_EVENT_TYPES = frozenset(
    {
        "system.health.degraded",
        "system.health.recovered",
        "ceo.priority",
        "campaign.fact.updated",
        "lead.spike",
        "hypothesis.review_due",
    }
)

SOURCE_BRAINS = frozenset({"koda", "vcms", "mb", "ceo_stub", "jadzia"})


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_inbound_event(body: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize Brain Bus inbound JSON."""
    event_type = (body.get("event_type") or "").strip()
    if event_type not in ALLOWED_EVENT_TYPES:
        raise ValueError(f"unsupported event_type: {event_type!r}")
    source = (body.get("source_brain") or "vcms").strip().lower()
    if source not in SOURCE_BRAINS:
        source = "vcms"
    payload = body.get("payload") if isinstance(body.get("payload"), dict) else {}
    corr = (body.get("correlation_id") or "").strip() or f"bb-{uuid.uuid4().hex[:12]}"
    return {
        "event_type": event_type,
        "source_brain": source,
        "payload": payload,
        "correlation_id": corr,
    }


def ingest_brain_bus_event(body: Dict[str, Any]) -> Dict[str, Any]:
    """Enqueue event onto SQLite brain_events bus."""
    event = normalize_inbound_event(body)
    eid = db_enqueue_brain_event(event)
    if eid is None:
        return {"ok": False, "error": "enqueue_failed", "event": event}
    logger.info(
        "[brain_bus] enqueued id=%s type=%s source=%s corr=%s",
        eid,
        event["event_type"],
        event["source_brain"],
        event["correlation_id"],
    )
    return {"ok": True, "event_id": eid, "event": event}


def _send_bus_telegram(message: str) -> bool:
    """Best-effort Telegram alert (same chat resolution as MB proposals)."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    admin_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "").strip()
    if not admin_id:
        allowed = os.getenv("ALLOWED_TELEGRAM_USERS", "").strip()
        if allowed:
            admin_id = allowed.split(",")[0].strip()
    if not bot_token or not admin_id:
        logger.warning("[brain_bus] telegram skipped — missing token/chat")
        return False
    try:
        import httpx

        r = httpx.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": admin_id, "text": message[:3500]},
            timeout=15.0,
        )
        ok = r.status_code == 200
        if not ok:
            logger.warning("[brain_bus] telegram HTTP %s", r.status_code)
        return ok
    except Exception as exc:
        logger.error("[brain_bus] telegram failed: %s", exc)
        return False


def handle_system_health_degraded(
    payload: Dict[str, Any],
    *,
    correlation_id: Optional[str] = None,
    source_brain: str = "vcms",
    send_telegram: bool = True,
) -> Dict[str, Any]:
    """
    Ecosystem red: quality flag + Commander ticket + Telegram.
    MB HOLD via CB_ECOSYSTEM (circuit_breakers).
    """
    conflicts = int(payload.get("conflicts") or payload.get("conflict_count") or 0)
    summary = (payload.get("summary") or payload.get("message") or "").strip()
    if not summary:
        summary = f"VCMS/KODA scan conflicts={conflicts}"
    details = {
        "conflicts": conflicts,
        "summary": summary,
        "correlation_id": correlation_id,
        "source_brain": source_brain,
        "repos": payload.get("repos") or payload.get("conflict_repos") or [],
        "as_of": _utc_now(),
    }
    flag_id = db_insert_quality_flag(
        {
            "flag_type": "ecosystem_red",
            "source": "vcms",
            "severity": "red",
            "message": f"Ecosystem health degraded: {summary[:200]}",
            "details": details,
        }
    )
    ticket_id = db_commander_create_ticket(
        title=f"[Brain Bus] Ecosystem RED conflicts={conflicts}",
        description=(
            f"source={source_brain}\n"
            f"correlation_id={correlation_id}\n"
            f"conflicts={conflicts}\n"
            f"{summary}\n"
            f"details={details}"
        ),
        source="brain_bus",
        severity="CRITICAL" if conflicts > 0 else "HIGH",
    )
    tg_ok = False
    if send_telegram:
        tg_ok = _send_bus_telegram(
            "🚨 Brain Bus — ecosystem RED\n"
            f"conflicts={conflicts}\n"
            f"{summary}\n"
            f"ticket_id={ticket_id}\n"
            f"corr={correlation_id}\n"
            "MB HOLD (CB_ECOSYSTEM) — no scale/execute."
        )
    logger.info(
        "[brain_bus] degraded flag=%s ticket=%s tg=%s conflicts=%s",
        flag_id,
        ticket_id,
        tg_ok,
        conflicts,
    )
    return {
        "ok": True,
        "action": "hold",
        "flag_id": flag_id,
        "ticket_id": ticket_id,
        "telegram_sent": tg_ok,
        "conflicts": conflicts,
    }


def handle_system_health_recovered(
    payload: Dict[str, Any],
    *,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Clear ecosystem_red flag when scan reports conflicts=0."""
    db_deactivate_quality_flags("vcms", "ecosystem_red")
    logger.info(
        "[brain_bus] recovered corr=%s payload_keys=%s",
        correlation_id,
        list(payload.keys()),
    )
    return {"ok": True, "action": "clear_hold", "correlation_id": correlation_id}


def handle_ceo_priority(
    payload: Dict[str, Any],
    *,
    correlation_id: Optional[str] = None,
    source_brain: str = "ceo_stub",
    send_telegram: bool = True,
) -> Dict[str, Any]:
    """CEO stub: persist priority as quality/info + optional Telegram (no Ads act)."""
    priority = (payload.get("priority") or payload.get("text") or "").strip()
    week = (payload.get("week") or "").strip()
    if not priority:
        return {"ok": False, "error": "missing_priority"}
    flag_id = db_insert_quality_flag(
        {
            "flag_type": "ceo_priority",
            "source": "ceo_stub",
            "severity": "amber",
            "message": f"CEO priority{(' ' + week) if week else ''}: {priority[:180]}",
            "details": {
                "priority": priority,
                "week": week,
                "correlation_id": correlation_id,
                "source_brain": source_brain,
            },
        }
    )
    ticket_id = db_commander_create_ticket(
        title=f"[CEO stub] Priority{(' · ' + week) if week else ''}",
        description=priority,
        source="brain_bus_ceo",
        severity="MEDIUM",
    )
    tg_ok = False
    if send_telegram:
        tg_ok = _send_bus_telegram(
            "📌 Brain Bus — CEO priority\n"
            f"{priority}\n"
            f"week={week or '—'}\n"
            f"ticket_id={ticket_id}\n"
            f"corr={correlation_id}"
        )
    return {
        "ok": True,
        "action": "priority_recorded",
        "flag_id": flag_id,
        "ticket_id": ticket_id,
        "telegram_sent": tg_ok,
    }


def publish_ceo_priority_stub(
    priority: str,
    *,
    week: Optional[str] = None,
    process_now: bool = True,
    send_telegram: bool = True,
) -> Dict[str, Any]:
    """Convenience: enqueue ceo.priority from brief/ops code paths."""
    body = {
        "event_type": "ceo.priority",
        "source_brain": "ceo_stub",
        "payload": {"priority": priority, "week": week or ""},
        "correlation_id": f"ceo-{uuid.uuid4().hex[:10]}",
    }
    enq = ingest_brain_bus_event(body)
    if not enq.get("ok"):
        return enq
    if process_now:
        from agent.marketing.brain_events import process_brain_events

        # Ensure telegram preference propagates via env-less call — process uses handlers
        result = process_brain_events(limit=5, send_telegram=send_telegram)
        enq["processed"] = result
    return enq
