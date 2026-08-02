"""Engage transports — mock (default smoke) + optional live stubs."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol


@dataclass
class ReadResult:
    ok: bool
    target_id: str
    platform: str
    items: List[Dict[str, Any]] = field(default_factory=list)
    mode: str = "mock"
    error: str = ""


@dataclass
class CommentResult:
    ok: bool
    target_id: str
    platform: str
    comment_id: str = ""
    mode: str = "mock"
    dry_run: bool = True
    error: str = ""


class EngageTransport(Protocol):
    def read(self, *, target_id: str, platform: str, external_id: str) -> ReadResult: ...

    def comment(
        self,
        *,
        target_id: str,
        platform: str,
        external_id: str,
        text: str,
        dry_run: bool,
    ) -> CommentResult: ...


class MockTransport:
    """Deterministic local smoke — no network. Default for F3 DoD."""

    def read(self, *, target_id: str, platform: str, external_id: str) -> ReadResult:
        return ReadResult(
            ok=True,
            target_id=target_id,
            platform=platform,
            mode="mock",
            items=[
                {
                    "id": f"mock_post_{target_id}",
                    "preview": f"[{platform}] allowlisted feed for {external_id or target_id}",
                }
            ],
        )

    def comment(
        self,
        *,
        target_id: str,
        platform: str,
        external_id: str,
        text: str,
        dry_run: bool,
    ) -> CommentResult:
        if not (text or "").strip():
            return CommentResult(
                ok=False,
                target_id=target_id,
                platform=platform,
                mode="mock",
                dry_run=dry_run,
                error="empty comment",
            )
        return CommentResult(
            ok=True,
            target_id=target_id,
            platform=platform,
            comment_id=f"mock_cmt_{target_id}",
            mode="mock",
            dry_run=dry_run,
        )


class LiveFacebookTransport:
    """
    Minimal live path: read own page feed when FB configured.
    Comments on groups stay mock/HITL until Graph group permissions + GO.
    Never posts without dry_run=False AND configured token.
    """

    def read(self, *, target_id: str, platform: str, external_id: str) -> ReadResult:
        if platform != "facebook":
            return ReadResult(
                ok=False,
                target_id=target_id,
                platform=platform,
                mode="live",
                error="live transport facebook-only in F3",
            )
        try:
            from agent.publishers.facebook import FACEBOOK_BASE, is_facebook_configured
            import requests

            if not is_facebook_configured():
                return ReadResult(
                    ok=False,
                    target_id=target_id,
                    platform=platform,
                    mode="live",
                    error="FB not configured",
                )
            page_id = os.getenv("FB_PAGE_ID", "")
            token = os.getenv("FB_ACCESS_TOKEN", "")
            ext = external_id
            if ext.startswith("env:"):
                ext = page_id
            url = f"{FACEBOOK_BASE}/{ext}/feed"
            resp = requests.get(
                url,
                params={"access_token": token, "limit": 3, "fields": "id,message,created_time"},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json().get("data") or []
            items = [
                {
                    "id": p.get("id"),
                    "preview": (p.get("message") or "")[:160],
                    "created_time": p.get("created_time"),
                }
                for p in data
            ]
            return ReadResult(
                ok=True,
                target_id=target_id,
                platform=platform,
                mode="live",
                items=items,
            )
        except Exception as exc:
            return ReadResult(
                ok=False,
                target_id=target_id,
                platform=platform,
                mode="live",
                error=str(exc)[:300],
            )

    def comment(
        self,
        *,
        target_id: str,
        platform: str,
        external_id: str,
        text: str,
        dry_run: bool,
    ) -> CommentResult:
        # F3: live group/page comments PARKED — use mock unless future GO LIVE COMMENT
        if dry_run or os.getenv("DEMAND_OS_LIVE_COMMENT") != "1":
            return MockTransport().comment(
                target_id=target_id,
                platform=platform,
                external_id=external_id,
                text=text,
                dry_run=True,
            )
        return CommentResult(
            ok=False,
            target_id=target_id,
            platform=platform,
            mode="live",
            dry_run=False,
            error="live comment not enabled (set DEMAND_OS_LIVE_COMMENT=1 + future GO)",
        )


class LiveTikTokTransport:
    """
    TT live stub — read/comment PARKED without secrets + DEMAND_OS_TT_LIVE=1.
    Default fail-closed; comments never auto-post (mirror FB park).
    """

    def read(self, *, target_id: str, platform: str, external_id: str) -> ReadResult:
        if platform != "tiktok":
            return ReadResult(
                ok=False,
                target_id=target_id,
                platform=platform,
                mode="live",
                error="LiveTikTokTransport tiktok-only",
            )
        if os.getenv("DEMAND_OS_TT_LIVE") != "1":
            return ReadResult(
                ok=False,
                target_id=target_id,
                platform=platform,
                mode="live",
                error="TT live disabled (DEMAND_OS_TT_LIVE!=1)",
            )
        if not (os.getenv("TIKTOK_ACCESS_TOKEN") or os.getenv("TT_ACCESS_TOKEN")):
            return ReadResult(
                ok=False,
                target_id=target_id,
                platform=platform,
                mode="live",
                error="missing TIKTOK_ACCESS_TOKEN",
            )
        return ReadResult(
            ok=False,
            target_id=target_id,
            platform=platform,
            mode="live",
            error="TT live read parked — use mock; no hunt",
        )

    def comment(
        self,
        *,
        target_id: str,
        platform: str,
        external_id: str,
        text: str,
        dry_run: bool,
    ) -> CommentResult:
        if dry_run or os.getenv("DEMAND_OS_LIVE_COMMENT") != "1":
            return MockTransport().comment(
                target_id=target_id,
                platform=platform,
                external_id=external_id,
                text=text,
                dry_run=True,
            )
        return CommentResult(
            ok=False,
            target_id=target_id,
            platform=platform,
            mode="live",
            dry_run=False,
            error="TT live comment PARKED (tool stub only)",
        )


def get_transport(mode: str = "mock", *, platform: str = "") -> EngageTransport:
    m = (mode or "mock").strip().lower()
    plat = (platform or "").strip().lower()
    if m == "live":
        if plat == "tiktok":
            return LiveTikTokTransport()
        return LiveFacebookTransport()
    return MockTransport()
