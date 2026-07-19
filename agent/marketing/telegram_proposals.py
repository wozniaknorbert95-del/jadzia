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


def build_mb_eval_keyboard(action_id: str) -> dict:
    """Eval-pack scoring (trust test) — separate from HITL approve/deny."""
    return {
        "inline_keyboard": [
            [
                {"text": "✅ Zgadzam się", "callback_data": f"mb_score_agree:{action_id}"},
                {"text": "🟡 Częściowo", "callback_data": f"mb_score_partial:{action_id}"},
            ],
            [
                {"text": "❌ Nie", "callback_data": f"mb_score_disagree:{action_id}"},
            ],
        ]
    }


def parse_mb_callback(callback_data: str) -> Optional[Tuple[str, str]]:
    """
    Returns (action, action_id) where action in
    approve|deny|details|score_agree|score_partial|score_disagree.
    """
    if not callback_data or ":" not in callback_data:
        return None
    prefix, _, rest = callback_data.partition(":")
    mapping = {
        "mb_approve": "approve",
        "mb_deny": "deny",
        "mb_details": "details",
        "mb_score_agree": "score_agree",
        "mb_score_partial": "score_partial",
        "mb_score_disagree": "score_disagree",
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
    Eval scores (score_*) go to marketing_shadow_eval — trust gate, not execute.
    """
    if action in ("score_agree", "score_partial", "score_disagree"):
        from agent.marketing.shadow_eval import compute_accuracy, record_eval_score

        score_map = {
            "score_agree": "agree",
            "score_partial": "partial",
            "score_disagree": "disagree",
        }
        result = record_eval_score(action_id, score_map[action])
        if not result.get("ok"):
            return {
                "ok": False,
                "message": result.get("error") or "score failed",
                "side_effect": False,
            }
        acc = compute_accuracy(window_days=14)
        acc_s = acc.get("accuracy")
        acc_txt = f"{acc_s:.0%}" if isinstance(acc_s, float) else "n/a"
        gate = "🟢 gate OK" if acc.get("gate_ready") else f"🔴 {acc.get('gate_reason')}"
        return {
            "ok": True,
            "message": (
                f"📝 Eval zapisane: {score_map[action]}\n"
                f"action_id={action_id}\n"
                f"14d accuracy={acc_txt} (n={acc.get('n_scored')}) {gate}"
            ),
            "side_effect": False,
            "accuracy": acc,
        }

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

    if action == "approve":
        from agent.marketing.governance import (
            approve_and_mint,
            format_approve_telegram_message,
        )

        status = row.get("hitl_status")
        if status == "executed_ticket":
            minted = approve_and_mint(action_id)
            row2 = db_get_marketing_shadow(action_id) or row
            return {
                "ok": True,
                "message": format_approve_telegram_message(minted, row2),
                "side_effect": False,
                "cached": True,
            }
        if status not in (None, "pending", "approved"):
            return {
                "ok": True,
                "message": (
                    f"Już rozpatrzone: {status} (action_id={action_id})."
                ),
                "side_effect": False,
            }

        minted = approve_and_mint(action_id)
        row2 = db_get_marketing_shadow(action_id) or row
        return {
            "ok": True,
            "message": format_approve_telegram_message(minted, row2),
            "side_effect": bool((minted.get("execute") or {}).get("ok")),
            "cached": bool(minted.get("cached")),
        }

    if row.get("hitl_status") not in (None, "pending"):
        return {
            "ok": True,
            "message": (
                f"Już rozpatrzone: {row.get('hitl_status')} "
                f"(action_id={action_id})."
            ),
            "side_effect": False,
        }

    if action == "deny":
        db_update_marketing_shadow_hitl(action_id, "denied", governance_result="deny")
        return {
            "ok": True,
            "message": f"❌ DENY zapisane. action_id={action_id}",
            "side_effect": False,
        }

    return {"ok": False, "message": "Nieznana akcja MB."}


def _telegram_admin_chat() -> Tuple[str, str]:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    admin_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "").strip()
    if not admin_id:
        allowed = os.getenv("ALLOWED_TELEGRAM_USERS", "").strip()
        if allowed:
            admin_id = allowed.split(",")[0].strip()
    return bot_token, admin_id


def send_eval_pack_telegram(*, limit: int = 10, window_days: int = 7) -> Dict[str, Any]:
    """Push stratified eval cards with score buttons (Telegram-first pack)."""
    from agent.marketing.shadow_eval import build_eval_pack, format_eval_card

    bot_token, admin_id = _telegram_admin_chat()
    if not bot_token or not admin_id:
        return {
            "ok": False,
            "error": "missing TELEGRAM_BOT_TOKEN or admin chat",
            "sent": 0,
        }

    pack = build_eval_pack(limit=limit, window_days=window_days, stratified=True)
    decisions = pack.get("decisions") or []
    if not decisions:
        return {
            "ok": True,
            "sent": 0,
            "message": "Brak niescorowanych decyzji w oknie — shadow musi najpierw coś zalogować.",
            "accuracy_snapshot": pack.get("accuracy_snapshot"),
        }

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    sent = 0
    errors = 0
    total = len(decisions)
    try:
        with httpx.Client(timeout=15.0) as client:
            for i, d in enumerate(decisions, start=1):
                aid = d.get("action_id") or ""
                text = format_eval_card(d, i, total)
                r = client.post(
                    url,
                    json={
                        "chat_id": admin_id,
                        "text": text,
                        "reply_markup": build_mb_eval_keyboard(aid),
                    },
                )
                if r.is_success:
                    sent += 1
                else:
                    errors += 1
                    logger.error(
                        "[mb.telegram] eval card failed action_id=%s status=%s",
                        aid,
                        r.status_code,
                    )
    except Exception as exc:
        logger.error("[mb.telegram] eval pack send failed: %s", exc)
        return {"ok": False, "error": str(exc), "sent": sent}

    acc = pack.get("accuracy_snapshot") or {}
    logger.info("[mb.telegram] eval pack sent=%s errors=%s", sent, errors)
    return {
        "ok": errors == 0,
        "sent": sent,
        "errors": errors,
        "n_pack": total,
        "accuracy_snapshot": acc,
        "message": f"Wysłano {sent}/{total} kart eval. Oceń przyciskami.",
    }


def send_staff_eval_summary_telegram(
    results: list,
    accuracy: Dict[str, Any],
) -> bool:
    """One plain-PL message: staff scored N cards + why (max ~8 lines)."""
    bot_token, admin_id = _telegram_admin_chat()
    if not bot_token or not admin_id:
        logger.warning("[mb.telegram] staff-eval summary skipped — no bot/admin")
        return False

    lines = [
        "🧠 Staff ocenił decyzje MB (za Ciebie — nie musisz klikać)",
        f"Ocena: {len(results)} kart",
    ]
    for r in results[:8]:
        score = r.get("eval_score") or "?"
        pl = r.get("pl") or ""
        rule = r.get("heuristic_rule_id") or "?"
        lines.append(f"• {score.upper()} | {rule}: {pl}")
    if len(results) > 8:
        lines.append(f"… i {len(results) - 8} więcej")

    acc_s = accuracy.get("accuracy")
    acc_txt = f"{acc_s:.0%}" if isinstance(acc_s, float) else "n/a"
    gate = "gotowe do propose" if accuracy.get("gate_ready") else "jeszcze zbieramy"
    lines.append(
        f"14d: accuracy={acc_txt} · n={accuracy.get('n_scored')}/20 · {gate}"
    )
    lines.append("Ty: Meta A1→A2→A3 (PLAN-14D / META-CLICK-PATH)")

    text = "\n".join(lines)
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        with httpx.Client(timeout=12.0) as client:
            r = client.post(url, json={"chat_id": admin_id, "text": text})
            r.raise_for_status()
        logger.info("[mb.telegram] staff-eval summary sent n=%s", len(results))
        return True
    except Exception as exc:
        logger.error("[mb.telegram] staff-eval summary failed: %s", exc)
        return False
