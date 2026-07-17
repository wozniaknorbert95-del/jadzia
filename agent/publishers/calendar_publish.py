"""Publish calendar row to Facebook by content_type."""

from __future__ import annotations

from typing import Dict

from agent.publishers.facebook import publish_photo, publish_post, publish_video


def publish_calendar_content(row: Dict) -> dict:
    """Route publish to text, photo, or video endpoint."""
    content_type = row.get("content_type") or "text"
    message = row.get("body_nl") or ""

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
