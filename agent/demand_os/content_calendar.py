"""content_calendar — structured week slots for TT/FB/Blog (OS §E MCP tool)."""

from __future__ import annotations

import json
import os
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

ALLOWED_STATUS = frozenset(
    {"planned", "validated", "blocked", "published", "skipped"}
)
ALLOWED_CHANNELS = frozenset({"tiktok", "facebook", "blog"})

_REPO = Path(__file__).resolve().parents[2]
DEFAULT_CALENDAR_PATH = _REPO / "docs/ops/demand-os/set-now/CONTENT-CALENDAR.json"


@dataclass
class CalendarSlot:
    date: str
    channel: str
    asset_id: str
    status: str = "planned"
    request_id: Optional[str] = None
    pass_token: Optional[str] = None
    notes: str = ""

    def __post_init__(self) -> None:
        self.channel = (self.channel or "").strip().lower()
        self.asset_id = (self.asset_id or "").strip()
        self.status = (self.status or "planned").strip().lower()
        if self.channel not in ALLOWED_CHANNELS:
            raise ValueError(f"channel not in calendar: {self.channel}")
        if self.status not in ALLOWED_STATUS:
            raise ValueError(f"status invalid: {self.status}")
        # validate ISO date
        date.fromisoformat(self.date)


@dataclass
class ContentCalendar:
    week: str
    slots: List[CalendarSlot] = field(default_factory=list)
    updated: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "week": self.week,
            "updated": self.updated,
            "slots": [asdict(s) for s in self.slots],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContentCalendar":
        slots = [CalendarSlot(**s) for s in (data.get("slots") or [])]
        return cls(
            week=str(data.get("week") or ""),
            updated=str(data.get("updated") or ""),
            slots=slots,
        )


def default_calendar_path() -> Path:
    env = os.environ.get("DEMAND_OS_CONTENT_CALENDAR")
    if env:
        return Path(env)
    return DEFAULT_CALENDAR_PATH


def load_calendar(path: Optional[Path] = None) -> ContentCalendar:
    src = path or default_calendar_path()
    if not src.is_file():
        return ContentCalendar(week="", slots=[], updated="")
    with src.open("r", encoding="utf-8") as fh:
        return ContentCalendar.from_dict(json.load(fh))


def save_calendar(cal: ContentCalendar, path: Optional[Path] = None) -> Path:
    from datetime import datetime, timezone

    dest = path or default_calendar_path()
    cal.updated = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8") as fh:
        json.dump(cal.to_dict(), fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return dest


def add_slot(
    cal: ContentCalendar,
    slot: CalendarSlot,
    *,
    replace_same_asset: bool = True,
) -> ContentCalendar:
    out = deepcopy(cal)
    if replace_same_asset:
        out.slots = [
            s
            for s in out.slots
            if not (s.asset_id == slot.asset_id and s.channel == slot.channel)
        ]
    out.slots.append(slot)
    out.slots.sort(key=lambda s: (s.date, s.channel, s.asset_id))
    return out


def set_slot_status(
    cal: ContentCalendar,
    *,
    asset_id: str,
    status: str,
    request_id: Optional[str] = None,
    pass_token: Optional[str] = None,
    notes: Optional[str] = None,
) -> ContentCalendar:
    status = status.strip().lower()
    if status not in ALLOWED_STATUS:
        raise ValueError(f"status invalid: {status}")
    out = deepcopy(cal)
    found = False
    for s in out.slots:
        if s.asset_id == asset_id:
            s.status = status
            if request_id is not None:
                s.request_id = request_id
            if pass_token is not None:
                s.pass_token = pass_token
            if notes is not None:
                s.notes = notes
            found = True
    if not found:
        raise KeyError(f"asset_id not in calendar: {asset_id}")
    return out


def list_slots(
    cal: ContentCalendar,
    *,
    channel: Optional[str] = None,
    status: Optional[str] = None,
) -> List[CalendarSlot]:
    rows = list(cal.slots)
    if channel:
        ch = channel.lower()
        rows = [s for s in rows if s.channel == ch]
    if status:
        st = status.lower()
        rows = [s for s in rows if s.status == st]
    return rows


def assert_publish_allowed(cal: ContentCalendar, asset_id: str) -> None:
    """Hard gate: publish only if slot validated + pass_token present."""
    matches = [s for s in cal.slots if s.asset_id == asset_id]
    if not matches:
        raise PermissionError(f"no calendar slot for {asset_id}")
    slot = matches[0]
    if slot.status != "validated":
        raise PermissionError(
            f"slot status={slot.status} - need validated (got no Val PASS)"
        )
    if not slot.pass_token:
        raise PermissionError(f"missing pass_token for {asset_id}")
