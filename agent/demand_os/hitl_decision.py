"""HITL publish decision — GOTOWY/BLOKADA to calendar + audit (never live publish)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from agent.demand_os.audit_log import append_audit
from agent.demand_os.content_calendar import (
    DEFAULT_CALENDAR_PATH,
    load_calendar,
    save_calendar,
    set_slot_status,
)

ALLOWED = frozenset({"GOTOWY", "BLOKADA"})


def record_hitl_decision(
    asset_id: str,
    decision: str,
    *,
    calendar_path: Optional[Path] = None,
    actor: str = "dowodca",
    notes: str = "",
) -> Dict[str, Any]:
    """
    GOTOWY → calendar status validated (Founder still publishes outside).
    BLOKADA → calendar status blocked.
    Does NOT publish to TT/FB.
    """
    dec = (decision or "").strip().upper()
    if dec not in ALLOWED:
        return {"ok": False, "error": f"decision must be GOTOWY|BLOKADA, got {decision}"}
    aid = (asset_id or "").strip()
    if not aid:
        return {"ok": False, "error": "asset_id required"}

    path = calendar_path or DEFAULT_CALENDAR_PATH
    cal = load_calendar(path=path)
    if not any(s.asset_id == aid for s in cal.slots):
        return {"ok": False, "error": f"asset_id not in calendar: {aid}", "live": False}

    new_status = "validated" if dec == "GOTOWY" else "blocked"
    try:
        updated = set_slot_status(
            cal,
            asset_id=aid,
            status=new_status,
            notes=notes or f"HITL {dec}",
        )
    except (ValueError, KeyError) as exc:
        return {"ok": False, "error": str(exc), "live": False}

    save_calendar(updated, path=path)
    slot = next(s for s in updated.slots if s.asset_id == aid)
    append_audit(
        "hitl_decision",
        actor=actor,
        detail={"asset_id": aid, "decision": dec, "calendar_status": new_status},
    )
    return {
        "ok": True,
        "asset_id": aid,
        "decision": dec,
        "calendar_status": new_status,
        "slot": {
            "asset_id": slot.asset_id,
            "channel": slot.channel,
            "status": slot.status,
            "notes": slot.notes,
        },
        "live": False,
        "publish": False,
        "marketing": "PARKED_LAST",
    }
