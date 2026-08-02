"""A2A publish_request — formal gate input for Sniper Validator (OS §E)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

CONTENT_TYPES = frozenset({"organic_post", "game_post", "reply"})
CHANNELS = frozenset(
    {"tiktok", "facebook", "blog", "whatsapp", "design_agent", "widget", "meta"}
)


@dataclass
class PublishRequest:
    """Single request to put content into the world (or engage reply)."""

    asset_id: str
    channel: str
    icp_role: str
    caption: str
    utm_link: str
    content_type: str = "organic_post"
    request_id: str = ""
    intended_publish_at: Optional[str] = None
    # Explicit risk flags (HITL / agent must set honestly)
    hero_is_hq: bool = False
    ads_boost: bool = False
    offerte_only: bool = False
    created_at: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.request_id:
            self.request_id = str(uuid4())
        if not self.created_at:
            self.created_at = (
                datetime.now(timezone.utc).replace(microsecond=0).isoformat()
            )
        self.channel = (self.channel or "").strip().lower()
        self.icp_role = (self.icp_role or "").strip().lower()
        self.asset_id = (self.asset_id or "").strip()
        self.content_type = (self.content_type or "organic_post").strip().lower()
        self.caption = self.caption or ""
        self.utm_link = (self.utm_link or "").strip()

    def validate_shape(self) -> list[str]:
        errors: list[str] = []
        if not self.asset_id:
            errors.append("asset_id required")
        if self.channel not in CHANNELS:
            errors.append(f"channel invalid: {self.channel}")
        if not self.icp_role:
            errors.append("icp_role required")
        if self.content_type not in CONTENT_TYPES:
            errors.append(f"content_type invalid: {self.content_type}")
        if self.content_type != "game_post" and not self.utm_link:
            errors.append("utm_link required for non-game content")
        if self.content_type != "game_post" and not self.caption.strip():
            errors.append("caption required")
        return errors

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PublishRequest":
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        payload = {k: v for k, v in (data or {}).items() if k in known}
        return cls(**payload)
