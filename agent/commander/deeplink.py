"""Signed deep-link tokens for mobile ticket access."""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from urllib.parse import urlencode

from agent.db import (
    db_commander_get_deeplink,
    db_commander_mark_deeplink_used,
    db_commander_save_deeplink,
)

DEEPLINK_TTL_MINUTES = 15


def _secret() -> bytes:
    return (os.getenv("JWT_SECRET") or "dev-deeplink-secret").encode()


def mint_deeplink(ticket_id: int, base_url: str, one_time: bool = False) -> Dict:
    exp = datetime.now(timezone.utc) + timedelta(minutes=DEEPLINK_TTL_MINUTES)
    nonce = secrets.token_urlsafe(16)
    payload = f"{ticket_id}:{int(exp.timestamp())}:{nonce}"
    sig = hmac.new(_secret(), payload.encode(), hashlib.sha256).hexdigest()
    token = f"{payload}:{sig}"
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    db_commander_save_deeplink(token_hash, ticket_id, exp.isoformat())
    qs = urlencode({"ticket": ticket_id, "token": token})
    url = f"{base_url.rstrip('/')}/commander/?{qs}"
    return {
        "url": url,
        "expires_at": exp.isoformat(),
        "ticket_id": ticket_id,
        "one_time": one_time,
    }


def verify_deeplink_token(token: str) -> Optional[int]:
    parts = token.split(":")
    if len(parts) != 4:
        return None
    ticket_id_s, exp_s, nonce, sig = parts
    payload = f"{ticket_id_s}:{exp_s}:{nonce}"
    expected = hmac.new(_secret(), payload.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        return None
    try:
        exp = datetime.fromtimestamp(int(exp_s), tz=timezone.utc)
    except (ValueError, OSError):
        return None
    if datetime.now(timezone.utc) > exp:
        return None
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    row = db_commander_get_deeplink(token_hash)
    if not row:
        return None
    if row.get("used_at"):
        return None
    db_commander_mark_deeplink_used(token_hash)
    return int(ticket_id_s)
