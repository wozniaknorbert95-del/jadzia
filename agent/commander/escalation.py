"""SLA breach detection and escalation to 2nd recipient (N6)."""

from __future__ import annotations

import json
import logging
import os
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage
from typing import Optional

from agent.commander.queue import build_queue
from agent.commander.settings import get_settings, touch_dowodca_activity
from agent.db import db_commander_get_setting, db_commander_set_setting

logger = logging.getLogger(__name__)

INACTIVE_HOURS = 24


def _send_telegram(msg: str, chat_id: Optional[str] = None) -> None:
    try:
        import httpx
        from threading import Thread

        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        target = chat_id or os.getenv("TELEGRAM_ADMIN_CHAT_ID")
        if not bot_token or not target:
            from agent.customer_agent import _send_telegram_alert_sync

            Thread(target=_send_telegram_alert_sync, args=(msg,), daemon=True).start()
            return

        def _run() -> None:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {"chat_id": target, "text": msg}
            with httpx.Client(timeout=10.0) as client_http:
                client_http.post(url, json=payload).raise_for_status()

        Thread(target=_run, daemon=True).start()
    except Exception as exc:
        logger.warning("[CommanderEscalation] TG notify failed: %s", exc)


def _send_delegat_email(subject: str, body: str, to_email: str) -> bool:
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587") or "587")
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    from_addr = os.getenv("SMTP_FROM", user or "jadzia@flexgrafik.nl")
    if not host or not to_email:
        logger.info("[CommanderEscalation] email skipped host=%s to=%s", host, to_email)
        return False
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = from_addr
        msg["To"] = to_email
        msg.set_content(body)
        with smtplib.SMTP(host, port, timeout=15) as smtp:
            if user and password:
                smtp.starttls()
                smtp.login(user, password)
            smtp.send_message(msg)
        return True
    except Exception as exc:
        logger.warning("[CommanderEscalation] email failed: %s", exc)
        return False


def _dowodca_inactive_hours() -> float:
    settings = get_settings()
    last = settings.get("dowodca_last_active_at")
    if not last:
        return INACTIVE_HOURS + 1
    try:
        dt = datetime.fromisoformat(str(last).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return INACTIVE_HOURS + 1
    return (datetime.now(timezone.utc) - dt).total_seconds() / 3600.0


def check_sla_escalations() -> int:
    """Return count of red items escalated. Called from worker loop."""
    touch_dowodca_activity("worker")
    settings = get_settings()
    delegat_email = settings.get("delegat_email") or ""
    delegat_tg = settings.get("delegat_telegram_chat_id") or ""
    inactive = _dowodca_inactive_hours() >= INACTIVE_HOURS
    escalated = 0

    for item in build_queue():
        if item.get("sla_status") != "red":
            continue
        key = f"escalated:{item['id']}"
        if db_commander_get_setting(key):
            continue

        msg = (
            f"SLA BREACH [{item['severity']}] {item['title']}\n"
            f"Age: {item['age_hours']}h\n"
            f"Delegat: {delegat_email or 'nie skonfigurowany'}"
        )
        _send_telegram(msg)

        if inactive and delegat_email:
            _send_delegat_email(
                f"COI Commander SLA breach: {item['title']}",
                msg,
                delegat_email,
            )
        if inactive and delegat_tg:
            _send_telegram(f"[Delegat] {msg}", chat_id=delegat_tg)

        db_commander_set_setting(key, json.dumps({"at": datetime.now(timezone.utc).isoformat()}))
        escalated += 1

    for agent in _silent_agents():
        key = f"escalated:agent:{agent['agent_id']}"
        if db_commander_get_setting(key):
            continue
        msg = f"Agent silent: {agent['label']} — SLA breach"
        _send_telegram(msg)
        if delegat_tg:
            _send_telegram(f"[Delegat] {msg}", chat_id=delegat_tg)
        db_commander_set_setting(key, json.dumps({"at": datetime.now(timezone.utc).isoformat()}))
        escalated += 1

    return escalated


def _silent_agents() -> list:
    from agent.commander.agents_registry import list_agents

    # None = untracked (HITL/on-demand) — not a silent-agent escalation.
    return [a for a in list_agents() if a.get("sla_ok") is False]
