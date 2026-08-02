"""Publish-path gate — Demand OS Val/calendar before any publisher (OS §E · §G)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from agent.demand_os.content_calendar import (
    ContentCalendar,
    assert_publish_allowed,
    load_calendar,
)


@dataclass
class GateDecision:
    allowed: bool
    asset_id: str
    reason: str
    pass_token: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "asset_id": self.asset_id,
            "reason": self.reason,
            "pass_token": self.pass_token,
        }


def check_publish_allowed(
    asset_id: str,
    *,
    calendar: Optional[ContentCalendar] = None,
    calendar_path: Optional[Path] = None,
) -> GateDecision:
    """ALLOW only when F2 calendar slot is validated + pass_token present."""
    aid = (asset_id or "").strip()
    if not aid:
        return GateDecision(False, "", "missing asset_id")
    cal = calendar or load_calendar(calendar_path)
    try:
        assert_publish_allowed(cal, aid)
    except PermissionError as exc:
        return GateDecision(False, aid, str(exc))
    slot = next((s for s in cal.slots if s.asset_id == aid), None)
    token = slot.pass_token if slot else None
    return GateDecision(True, aid, "GATE ALLOW", pass_token=token)


def gated_publish_calendar_content(
    row: Dict[str, Any],
    *,
    calendar_path: Optional[Path] = None,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """
    Bridge into agent.publishers.calendar_publish with Demand OS gate.
    dry_run=True (default): never hits live publishers — returns ALLOW/DENY only.
    """
    asset_id = (
        (row.get("asset_id") or row.get("content_id") or row.get("id") or "")
    ).strip()
    decision = check_publish_allowed(asset_id, calendar_path=calendar_path)
    try:
        from agent.demand_os.audit_log import append_audit

        append_audit(
            "gate_allow" if decision.allowed else "gate_deny",
            actor="Publish_Gate",
            detail={"asset_id": asset_id, "reason": decision.reason, "dry_run": dry_run},
        )
    except Exception:
        pass
    if not decision.allowed:
        return {
            "status": "denied",
            "error": decision.reason,
            "gate": decision.to_dict(),
            "dry_run": dry_run,
        }
    if dry_run:
        return {
            "status": "ok",
            "dry_run": True,
            "gate": decision.to_dict(),
            "message": "GATE ALLOW — live publish skipped (dry_run)",
        }
    from agent.publishers.calendar_publish import publish_calendar_content

    result = publish_calendar_content(row)
    result["gate"] = decision.to_dict()
    return result
