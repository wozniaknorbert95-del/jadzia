"""Facebook Graph API publisher — INT-011."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)

FACEBOOK_API_VERSION = "v25.0"
FACEBOOK_BASE = f"https://graph.facebook.com/{FACEBOOK_API_VERSION}"


def is_facebook_configured() -> bool:
    """Return True when FB_PAGE_ID and FB_ACCESS_TOKEN are set."""
    return bool(os.getenv("FB_PAGE_ID") and os.getenv("FB_ACCESS_TOKEN"))


def _get_config() -> tuple[str, str]:
    page_id = os.getenv("FB_PAGE_ID")
    access_token = os.getenv("FB_ACCESS_TOKEN")
    if not page_id or not access_token:
        raise RuntimeError("FB_PAGE_ID and FB_ACCESS_TOKEN required in .env")
    return page_id, access_token


def publish_post(message: str, scheduled_publish_time: Optional[int] = None) -> dict:
    """Publish a text post to the configured Facebook Page.

    Args:
        message: Post body text.
        scheduled_publish_time: Unix timestamp for scheduled publish (optional).

    Returns:
        dict with status success|error, post_id on success, error details on failure.
    """
    page_id, access_token = _get_config()
    url = f"{FACEBOOK_BASE}/{page_id}/feed"

    payload: dict[str, str] = {
        "message": message,
        "access_token": access_token,
    }
    if scheduled_publish_time is not None:
        payload["published"] = "false"
        payload["scheduled_publish_time"] = str(scheduled_publish_time)

    try:
        resp = requests.post(url, data=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        post_id = data.get("id")
        logger.info(
            "[FacebookPublisher] Published post_id=%s scheduled=%s",
            post_id,
            bool(scheduled_publish_time),
        )
        return {
            "status": "success",
            "post_id": post_id,
            "scheduled": bool(scheduled_publish_time),
        }
    except requests.RequestException as exc:
        details = None
        response = getattr(exc, "response", None)
        if response is not None:
            details = response.text
        logger.error("[FacebookPublisher] Publish failed: %s", exc)
        return {
            "status": "error",
            "error": str(exc),
            "details": details,
        }


def publish_photo(
    message: str,
    image_url: str,
    scheduled_publish_time: Optional[int] = None,
) -> dict:
    """Publish a photo post to Facebook Page using a remote image URL."""
    page_id, access_token = _get_config()
    url = f"{FACEBOOK_BASE}/{page_id}/photos"

    payload: dict[str, str] = {
        "message": message,
        "url": image_url,
        "access_token": access_token,
    }
    if scheduled_publish_time is not None:
        payload["published"] = "false"
        payload["scheduled_publish_time"] = str(scheduled_publish_time)

    try:
        resp = requests.post(url, data=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        post_id = data.get("post_id") or data.get("id")
        logger.info(
            "[FacebookPublisher] Published photo post_id=%s scheduled=%s",
            post_id,
            bool(scheduled_publish_time),
        )
        return {
            "status": "success",
            "post_id": post_id,
            "scheduled": bool(scheduled_publish_time),
        }
    except requests.RequestException as exc:
        details = None
        response = getattr(exc, "response", None)
        if response is not None:
            details = response.text
        logger.error("[FacebookPublisher] Photo publish failed: %s", exc)
        return {
            "status": "error",
            "error": str(exc),
            "details": details,
        }


def check_post_status(post_id: str) -> dict:
    """Fetch post metadata from Graph API."""
    _, access_token = _get_config()
    url = f"{FACEBOOK_BASE}/{post_id}"

    try:
        resp = requests.get(
            url,
            params={
                "access_token": access_token,
                "fields": "id,message,created_time,is_published,scheduled_publish_time",
            },
            timeout=15,
        )
        resp.raise_for_status()
        return {"status": "success", "data": resp.json()}
    except requests.RequestException as exc:
        logger.error("[FacebookPublisher] Status check failed post_id=%s: %s", post_id, exc)
        return {"status": "error", "error": str(exc)}


def parse_publish_error(result: Dict[str, Any]) -> str:
    """Map Graph API / publish errors to operator-facing PL messages."""
    if not result or result.get("status") == "success":
        return ""

    raw_error = str(result.get("error") or result.get("message") or "")
    details_raw = result.get("details")
    fb_error: Dict[str, Any] = {}
    if details_raw:
        try:
            parsed = json.loads(details_raw) if isinstance(details_raw, str) else details_raw
            fb_error = (parsed.get("error") or {}) if isinstance(parsed, dict) else {}
        except (json.JSONDecodeError, TypeError, AttributeError):
            fb_error = {}

    code = fb_error.get("code")
    subcode = fb_error.get("error_subcode")
    msg = str(fb_error.get("message") or raw_error)

    if code == 190 or subcode == 463 or "Session has expired" in msg or "expired" in msg.lower():
        return "Token Facebook wygasł — odśwież Page Token FlexGrafik"
    if "publish_actions" in msg or "USER" in msg.upper():
        return "Wymagany Page Token FlexGrafik (nie User Token z Graph Explorer)"
    if code == 200 and "permission" in msg.lower():
        return "Brak uprawnień pages_manage_posts — sprawdź token strony"
    if "url" in msg.lower() or "photo" in msg.lower() or "image" in msg.lower():
        return "Meta nie pobrała grafiki — sprawdź udostępnianie pliku na Drive"
    if "Brak media_url" in raw_error:
        return "Brak linku do grafiki w wpisie"
    if raw_error:
        return raw_error[:200]
    return "Publikacja na Facebooku nie powiodła się"


def check_token_health() -> Dict[str, Any]:
    """Preflight FB token — type, expiry, no secret in response."""
    if not is_facebook_configured():
        return {
            "ok": False,
            "configured": False,
            "message_pl": "Facebook nie skonfigurowany (FB_PAGE_ID / FB_ACCESS_TOKEN)",
        }

    _, access_token = _get_config()
    try:
        resp = requests.get(
            f"{FACEBOOK_BASE}/debug_token",
            params={"input_token": access_token, "access_token": access_token},
            timeout=15,
        )
        resp.raise_for_status()
        data = (resp.json() or {}).get("data") or {}
    except requests.RequestException as exc:
        logger.warning("[FacebookPublisher] Token health check failed: %s", exc)
        return {
            "ok": False,
            "configured": True,
            "message_pl": "Nie udało się sprawdzić tokenu Facebook",
        }

    token_type = data.get("type") or "UNKNOWN"
    expires_at = data.get("expires_at")
    days_left: Optional[int] = None
    if expires_at:
        try:
            exp_dt = datetime.fromtimestamp(int(expires_at), tz=timezone.utc)
            days_left = max(0, int((exp_dt - datetime.now(timezone.utc)).total_seconds() / 86400))
        except (ValueError, TypeError, OSError):
            days_left = None

    ok = data.get("is_valid") and token_type == "PAGE"
    message_pl = "Token OK (Page)"
    if not data.get("is_valid"):
        message_pl = "Token Facebook nieważny"
    elif token_type != "PAGE":
        message_pl = "To nie jest Page Token — użyj FlexGrafik Page Token"
    elif days_left is not None and days_left < 7:
        message_pl = f"Token wygasa za {days_left} dni — zaplanuj rotację"

    return {
        "ok": ok,
        "configured": True,
        "token_type": token_type,
        "expires_at": expires_at,
        "days_left": days_left,
        "message_pl": message_pl,
        "page_id": os.getenv("FB_PAGE_ID"),
    }


def delete_post(post_id: str) -> dict:
    """Delete a post (E2E cleanup)."""
    _, access_token = _get_config()
    url = f"{FACEBOOK_BASE}/{post_id}"

    try:
        resp = requests.delete(
            url,
            params={"access_token": access_token},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        logger.info("[FacebookPublisher] Deleted post_id=%s success=%s", post_id, data.get("success"))
        return {"status": "success", "data": data}
    except requests.RequestException as exc:
        logger.error("[FacebookPublisher] Delete failed post_id=%s: %s", post_id, exc)
        return {"status": "error", "error": str(exc)}
