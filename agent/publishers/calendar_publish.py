"""Publish calendar row to Facebook or TikTok by platform + content_type."""

from __future__ import annotations

from typing import Dict

from agent.publishers.facebook import publish_photo, publish_post, publish_video
from agent.publishers import tiktok as tt


def publish_calendar_content(row: Dict) -> dict:
    """Route publish to the correct platform publisher."""
    platform = (row.get("platform") or "facebook").strip().lower()
    content_type = row.get("content_type") or "text"
    message = row.get("body_nl") or ""

    if platform == "tiktok":
        if content_type != "video":
            return {
                "status": "error",
                "error": "TikTok calendar publish supports content_type=video only",
            }
        media_url = row.get("media_url")
        if not media_url:
            return {"status": "error", "error": "Brak media_url dla wpisu TikTok wideo"}
        return tt.publish_video(message, media_url)

    if content_type == "video":
        media_url = row.get("media_url")
        if not media_url:
            return {"status": "error", "error": "Brak media_url dla wpisu wideo"}
        return publish_video(message, media_url)

    if content_type == "image":
        media_url = row.get("media_url")
        if not media_url:
            return {"status": "error", "error": "Brak media_url dla wpisu graficznego"}
        return publish_photo(message, media_url)

    return publish_post(message)
