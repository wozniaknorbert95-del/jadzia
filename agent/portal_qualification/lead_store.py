"""Persist portal qualification leads to jadzia.db (GDPR: consent required)."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from agent.db import db_transaction

logger = logging.getLogger(__name__)

RETENTION_MONTHS = 24


def save_portal_qual_lead(
    *,
    session_id: str,
    profile: Dict[str, Optional[str]],
    recommended_preset_id: str,
    source: str = "portal_qual",
) -> bool:
    """Insert qualified lead. Returns True on success."""
    if not session_id or not recommended_preset_id:
        return False

    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=RETENTION_MONTHS * 30)
    created_at = now.isoformat()
    expires_at = expires.isoformat()

    try:
        with db_transaction() as conn:
            conn.execute(
                """
                INSERT INTO portal_qual_leads (
                    session_id, industry, goal, vehicle, budget_tier,
                    recommended_preset_id, source, consent, created_at, expires_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
                """,
                (
                    session_id,
                    profile.get("industry"),
                    profile.get("goal"),
                    profile.get("vehicle"),
                    profile.get("budget_tier"),
                    recommended_preset_id,
                    source,
                    created_at,
                    expires_at,
                ),
            )
        logger.info(
            "[PortalQual] Lead saved session=%s preset=%s",
            session_id[:8],
            recommended_preset_id,
        )
        _maybe_hot_lead_alert(profile, recommended_preset_id)
        return True
    except Exception as e:
        logger.error("[PortalQual] Lead save failed: %s", e, exc_info=True)
        return False


def _maybe_hot_lead_alert(profile: Dict[str, Optional[str]], preset_id: str) -> None:
    budget = profile.get("budget_tier")
    if preset_id != "professional-flota" and budget != "700_plus":
        return
    try:
        from threading import Thread

        from agent.customer_agent import _send_telegram_alert_sync

        summary = json.dumps(profile, ensure_ascii=False)
        msg = (
            f"🔥 <b>PORTAL QUAL LEAD</b>\n"
            f"<b>Preset:</b> {preset_id}\n"
            f"<b>Profiel:</b> <code>{summary}</code>"
        )
        Thread(target=_send_telegram_alert_sync, args=(msg,), daemon=True).start()
    except Exception as e:
        logger.warning("[PortalQual] Hot lead alert skipped: %s", e)
