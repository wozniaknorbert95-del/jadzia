"""Telegram-first MB proposals — shadow HITL (no side-effects on approve)."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional, Tuple

import httpx

from agent.db import (
    db_get_marketing_shadow,
    db_update_marketing_shadow_hitl,
)
from agent.marketing.heuristics import Decision

logger = logging.getLogger(__name__)


def build_mb_inline_keyboard(action_id: str) -> dict:
    return {
        "inline_keyboard": [
            [
                {"text": "✅ APPROVE", "callback_data": f"mb_approve:{action_id}"},
                {"text": "❌ DENY", "callback_data": f"mb_deny:{action_id}"},
            ],
            [
                {"text": "📊 DETAILS", "callback_data": f"mb_details:{action_id}"},
            ],
        ]
    }


def parse_mb_callback(callback_data: str) -> Optional[Tuple[str, str]]:
    """
    Returns (action, action_id) where action in approve|deny|details.
    """
    if not callback_data or ":" not in callback_data:
        return None
    prefix, _, rest = callback_data.partition(":")
    mapping = {
        "mb_approve": "approve",
        "mb_deny": "deny",
        "mb_details": "details",
    }
    if prefix not in mapping or not rest.strip():
        return None
    return mapping[prefix], rest.strip()


def format_proposal_text(
    action_id: str,
    decision: Decision,
    mb_mode: str,
) -> str:
    mode_tag = "SHADOW — nie wykonano" if mb_mode == "shadow" else mb_mode.upper()
    return (
        f"🧠 Marketing Brain [{mode_tag}]\n"
        f"Rule: {decision.heuristic_rule_id}\n"
        f"Action: {decision.proposed_action}\n"
        f"Severity: {decision.severity}\n"
        f"{decision.rationale_nl}\n"
        f"action_id={action_id}"
    )


def send_mb_proposal_telegram(
    action_id: str,
    decision: Decision,
    mb_mode: str,
) -> bool:
    """Send proposal with inline buttons to TELEGRAM_ADMIN_CHAT_ID."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    admin_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "").strip()
    if not admin_id:
        # Fallback: first allowlisted Dowódca user_id (same chat for private bots)
        allowed = os.getenv("ALLOWED_TELEGRAM_USERS", "").strip()
        if allowed:
            admin_id = allowed.split(",")[0].strip()
    if not bot_token or not admin_id:
        logger.warning(
            "[mb.telegram] skipped — missing TELEGRAM_BOT_TOKEN or admin chat "
            "(TELEGRAM_ADMIN_CHAT_ID / ALLOWED_TELEGRAM_USERS)"
        )
        return False
    text = format_proposal_text(action_id, decision, mb_mode)
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": admin_id,
        "text": text,
        "reply_markup": build_mb_inline_keyboard(action_id),
    }
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.post(url, json=payload)
            r.raise_for_status()
        logger.info("[mb.telegram] proposal sent action_id=%s", action_id)
        return True
    except Exception as exc:
        logger.error("[mb.telegram] send failed action_id=%s: %s", action_id, exc)
        return False


def handle_mb_hitl(action: str, action_id: str) -> Dict[str, Any]:
    """
    Process Telegram HITL for MB proposal.
    F1 shadow: APPROVE/DENY only update shadow_log — no Ads/publish side-effects.
    """
    row = db_get_marketing_shadow(action_id)
    if not row:
        return {
            "ok": False,
            "message": f"Nie znam action_id={action_id} (wygasło lub brak).",
        }

    if action == "details":
        payload = row.get("payload") or {}
        facts = payload.get("facts_summary") or {}
        msg = (
            f"📊 DETAILS {action_id}\n"
            f"rule={row.get('heuristic_rule_id')}\n"
            f"action={row.get('proposed_action')}\n"
            f"mode={row.get('mb_mode')}\n"
            f"hitl={row.get('hitl_status')}\n"
            f"margin_avg={facts.get('margin_avg_pct')}\n"
            f"attr_coverage={facts.get('attribution_coverage_pct')}\n"
            f"red_flags={facts.get('red_flags')}\n"
            f"Commander: /commander/ → Analityka → Data Health"
        )
        return {"ok": True, "message": msg, "side_effect": False}

    if row.get("hitl_status") not in (None, "pending"):
        return {
            "ok": True,
            "message": (
                f"Już rozpatrzone: {row.get('hitl_status')} "
                f"(action_id={action_id})."
            ),
            "side_effect": False,
        }

    if action == "approve":
        from agent.marketing.governance import approve_and_mint

        minted = approve_and_mint(action_id)
        mode = row.get("mb_mode") or "shadow"
        if mode == "shadow":
            return {
                "ok": True,
                "message": (
                    f"✅ APPROVE zapisane (SHADOW — nie wykonano side-effect).\n"
                    f"Token zmintowany (TTL 15m) — execute zablokowany przez CB_SHADOW.\n"
                    f"action_id={action_id}"
                ),
                "side_effect": False,
                "approval_token_minted": bool(minted.get("approval_token")),
            }
        # propose/act: token available for Governance execute endpoint
        return {
            "ok": True,
            "message": (
                f"✅ APPROVE + token (TTL 15m).\n"
                f"POST /api/v1/marketing/actions/execute\n"
                f"action_id={action_id}"
            ),
            "side_effect": False,
            "approval_token": minted.get("approval_token"),
        }

    if action == "deny":
        db_update_marketing_shadow_hitl(action_id, "denied", governance_result="deny")
        return {
            "ok": True,
            "message": f"❌ DENY zapisane. action_id={action_id}",
            "side_effect": False,
        }

    return {"ok": False, "message": "Nieznana akcja MB."}
