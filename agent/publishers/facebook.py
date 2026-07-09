"""Facebook Graph API publisher — INT-011."""

from __future__ import annotations

import logging
import os
from typing import Optional

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
