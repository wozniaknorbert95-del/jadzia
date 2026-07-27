"""INSPIRE offerte concierge — lead capture after mockup selection."""

from __future__ import annotations

import json
import logging
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from agent.commander.escalation import _send_delegat_email
from agent.customer_agent import _send_telegram_alert_sync
from agent.db import db_offerte_find_recent, db_offerte_insert
from agent.inspire.chat_locale import normalize_locale
from agent.rate_store import check_and_record
from threading import Thread

logger = logging.getLogger(__name__)

_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def _offerte_rate_limit() -> int:
    try:
        return max(3, int(os.getenv("DA_OFFERTE_RATE_LIMIT", "10")))
    except ValueError:
        return 10


def _team_email() -> str:
    return (os.getenv("OFFERTE_TEAM_EMAIL") or os.getenv("SMTP_FROM") or "").strip()


def _new_offerte_id() -> str:
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    short = uuid.uuid4().hex[:8]
    return f"off-{day}-{short}"


def _validate_payload(body: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    contact = body.get("contact") or {}
    selection = body.get("selection") or {}
    email = str(contact.get("email") or "").strip().lower()
    telefoon = str(contact.get("telefoon") or "").strip()
    consent = bool(contact.get("consent_offerte"))
    variant = str(selection.get("variant") or "").strip().lower()
    sku = str(selection.get("sku") or "").strip()
    session_id = str(body.get("session_id") or "").strip()

    if not session_id:
        return {}, "session_id required"
    if not email or not _EMAIL_RE.match(email):
        return {}, "invalid email"
    if len(telefoon) < 8:
        return {}, "invalid telefoon"
    if not consent:
        return {}, "consent_offerte required"
    if variant not in ("standard", "premium"):
        return {}, "invalid variant"
    if not sku:
        return {}, "sku required"

    normalized = {
        "session_id": session_id,
        "locale": normalize_locale(body.get("locale")),
        "email": email,
        "telefoon": telefoon,
        "variant": variant,
        "sku": sku,
        "payload_json": json.dumps(body, ensure_ascii=False),
    }
    return normalized, None


def _telegram_message(row: dict[str, Any], body: dict[str, Any]) -> str:
    brief = body.get("brief_partial") or {}
    selection = body.get("selection") or {}
    bedrijf = brief.get("bedrijfsnaam") or "—"
    mockup = selection.get("mockup_url") or "—"
    return (
        f"🧾 INSPIRE Offerte\n"
        f"ID: {row['id']}\n"
        f"Bedrijf: {bedrijf}\n"
        f"Variant: {row['variant']} · SKU: {row['sku']}\n"
        f"Tel: {row['telefoon']}\n"
        f"E-mail: {row['email']}\n"
        f"Mockup: {mockup}\n"
        f"Session: {row['session_id']}"
    )


def _client_email_body(offerte_id: str) -> str:
    return (
        f"Bedankt voor je offerte-aanvraag bij FlexGrafik.\n\n"
        f"Referentie: {offerte_id}\n\n"
        f"Je ontvangt binnen 48 werkdagen een vrijblijvende, persoonlijke offerte per e-mail "
        f"en telefoon. Geen betaling nu — en geen drukklare bestanden vanuit de AI-mock-up.\n\n"
        f"Met vriendelijke groet,\nFlexGrafik"
    )


def _team_email_body(row: dict[str, Any], body: dict[str, Any]) -> str:
    return (
        f"INSPIRE offerte request\n\n"
        f"ID: {row['id']}\n"
        f"Session: {row['session_id']}\n"
        f"Variant: {row['variant']}\n"
        f"SKU: {row['sku']}\n"
        f"Contact: {row['email']} / {row['telefoon']}\n\n"
        f"Payload:\n{row['payload_json']}"
    )


def create_offerte_request(body: dict[str, Any], *, client_ip: str = "unknown") -> dict[str, Any]:
    normalized, err = _validate_payload(body)
    if err:
        raise ValueError(err)

    session_id = normalized["session_id"]
    sku = normalized["sku"]

    dup = db_offerte_find_recent(session_id, sku, within_sec=3600)
    if dup:
        return {
            "ok": True,
            "offerte_request_id": dup["id"],
            "message_nl": "Bedankt — je offerte-aanvraag is al ontvangen.",
            "duplicate": True,
        }

    try:
        check_and_record(
            f"offerte:session:{session_id}",
            window_sec=86400,
            limit=3,
        )
        check_and_record(
            f"offerte:ip:{client_ip}",
            window_sec=86400,
            limit=_offerte_rate_limit(),
        )
    except ValueError as exc:
        if str(exc) == "RATE_LIMIT":
            raise ValueError("rate_limit") from exc
        raise

    offerte_id = _new_offerte_id()
    now = datetime.now(timezone.utc).isoformat()
    row = {
        "id": offerte_id,
        "session_id": session_id,
        "email": normalized["email"],
        "telefoon": normalized["telefoon"],
        "variant": normalized["variant"],
        "sku": sku,
        "payload_json": normalized["payload_json"],
        "status": "new",
        "notify_team": "pending",
        "notify_client": "pending",
        "created_at": now,
    }
    db_offerte_insert(row)

    tg_msg = _telegram_message(row, body)
    Thread(target=_send_telegram_alert_sync, args=(tg_msg,), daemon=True).start()

    team_ok = False
    team_email = _team_email()
    if team_email:
        team_ok = _send_delegat_email(
            f"[INSPIRE Offerte] {offerte_id}",
            _team_email_body(row, body),
            team_email,
        )

    client_ok = _send_delegat_email(
        f"Offerte-aanvraag ontvangen — {offerte_id}",
        _client_email_body(offerte_id),
        normalized["email"],
    )

    notify_team = "ok" if team_ok else "pending"
    notify_client = "ok" if client_ok else "pending"
    from agent.db import db_offerte_update_notify

    db_offerte_update_notify(offerte_id, notify_team=notify_team, notify_client=notify_client)

    return {
        "ok": True,
        "offerte_request_id": offerte_id,
        "message_nl": "Bedankt — je offerte-aanvraag is ontvangen.",
        "notify_team": notify_team,
        "notify_client": notify_client,
    }
