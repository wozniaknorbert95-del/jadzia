"""TikTok Content Posting API publisher — TT-PUB-01 (parity with facebook.py).

Direct Post via PULL_FROM_URL. Requires Developer app + OAuth token with
``video.publish``. Domain/URL prefix for media_url must be verified in TikTok
Developer console. No RPA / Studio browser automation here.
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)

TIKTOK_API_BASE = "https://open.tiktokapis.com"
TIKTOK_VIDEO_INIT = f"{TIKTOK_API_BASE}/v2/post/publish/video/init/"
TIKTOK_STATUS_FETCH = f"{TIKTOK_API_BASE}/v2/post/publish/status/fetch/"


def _redact_secrets(text: str) -> str:
    if not text:
        return text
    out = re.sub(
        r"(Bearer\s+)([A-Za-z0-9._\-]+)",
        r"\1REDACTED",
        str(text),
        flags=re.IGNORECASE,
    )
    out = re.sub(r"act\.[A-Za-z0-9._\-]+", "REDACTED_TOKEN", out)
    return out


def is_tiktok_configured() -> bool:
    """True when access token is set (open_id optional for Direct Post Bearer)."""
    return bool(os.getenv("TIKTOK_ACCESS_TOKEN", "").strip())


def _get_access_token() -> str:
    token = os.getenv("TIKTOK_ACCESS_TOKEN", "").strip()
    if not token:
        raise RuntimeError("TIKTOK_ACCESS_TOKEN required in .env")
    return token


def _default_privacy() -> str:
    return (
        os.getenv("TIKTOK_DEFAULT_PRIVACY", "PUBLIC_TO_EVERYONE").strip()
        or "PUBLIC_TO_EVERYONE"
    )


def publish_video(
    title: str,
    video_url: str,
    privacy_level: Optional[str] = None,
) -> dict:
    """Init Direct Post with PULL_FROM_URL (TikTok fetches video_url).

    Returns:
        ``{status, post_id, publish_id, ...}`` on success (post_id == publish_id),
        or ``{status: error, error, details}``.
    """
    access_token = _get_access_token()
    if not video_url or not str(video_url).startswith("https://"):
        return {
            "status": "error",
            "error": "TikTok requires https media_url (PULL_FROM_URL)",
        }

    payload: Dict[str, Any] = {
        "post_info": {
            "title": (title or "")[:2200],
            "privacy_level": privacy_level or _default_privacy(),
            "disable_duet": False,
            "disable_comment": False,
            "disable_stitch": False,
        },
        "source_info": {
            "source": "PULL_FROM_URL",
            "video_url": video_url,
        },
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8",
    }

    try:
        resp = requests.post(
            TIKTOK_VIDEO_INIT,
            headers=headers,
            json=payload,
            timeout=60,
        )
        data = resp.json() if resp.content else {}
        err_code = (data.get("error") or {}).get("code") or ""
        if resp.status_code >= 400 or (err_code and err_code != "ok"):
            logger.error(
                "[TikTokPublisher] Init failed status=%s body=%s",
                resp.status_code,
                _redact_secrets(resp.text[:500] if resp.text else ""),
            )
            return {
                "status": "error",
                "error": _redact_secrets(
                    (data.get("error") or {}).get("message")
                    or f"HTTP {resp.status_code}"
                ),
                "details": _redact_secrets(resp.text[:1000] if resp.text else ""),
            }

        publish_id = (data.get("data") or {}).get("publish_id")
        logger.info("[TikTokPublisher] Init ok publish_id=%s", publish_id)
        return {
            "status": "success",
            "post_id": publish_id,
            "publish_id": publish_id,
            "platform": "tiktok",
        }
    except requests.RequestException as exc:
        details = None
        response = getattr(exc, "response", None)
        if response is not None:
            details = _redact_secrets(response.text[:1000] if response.text else "")
        logger.error(
            "[TikTokPublisher] Publish failed: %s",
            _redact_secrets(str(exc)),
        )
        return {
            "status": "error",
            "error": _redact_secrets(str(exc)),
            "details": details,
        }


def fetch_publish_status(publish_id: str) -> dict:
    """Poll ``/v2/post/publish/status/fetch/`` for a publish_id."""
    access_token = _get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8",
    }
    try:
        resp = requests.post(
            TIKTOK_STATUS_FETCH,
            headers=headers,
            json={"publish_id": publish_id},
            timeout=30,
        )
        data = resp.json() if resp.content else {}
        if resp.status_code >= 400:
            return {
                "status": "error",
                "error": _redact_secrets(resp.text[:500] if resp.text else ""),
            }
        return {"status": "success", "data": data.get("data") or data}
    except requests.RequestException as exc:
        return {"status": "error", "error": _redact_secrets(str(exc))}


def parse_publish_error(result: dict) -> str:
    """Short PL message for Commander / Telegram."""
    if not result or result.get("status") == "success":
        return ""
    err = str(result.get("error") or result.get("details") or "TikTok publish failed")
    return _redact_secrets(err)[:300]


def check_token_health() -> dict:
    """Lightweight config presence check (no live TikTok call without token)."""
    configured = is_tiktok_configured()
    return {
        "configured": configured,
        "has_open_id": bool(os.getenv("TIKTOK_OPEN_ID", "").strip()),
        "privacy_default": _default_privacy() if configured else None,
        "status": "ok" if configured else "missing_token",
    }
