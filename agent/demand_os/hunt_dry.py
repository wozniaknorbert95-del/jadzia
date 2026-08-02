"""Hunt dry engage — B2 Desk (mock comment + ENGAGE-LOG, no live)."""

from __future__ import annotations

from typing import Any, Dict, Optional

from agent.demand_os.connectors.engage import comment_on_target
from agent.demand_os.utm_lock import build_wizard_utm


def run_hunt_dry(
    target_id: str,
    *,
    text: str = "",
    icp_role: str = "installateur",
    asset_id: str = "hunt_dry",
) -> Dict[str, Any]:
    """Dry comment on allowlist target; persists ENGAGE-LOG for hunt_queue."""
    tid = (target_id or "").strip()
    if not tid:
        return {"ok": False, "error": "target_id required", "live": False}

    body = (text or "").strip()
    if not body:
        utm = build_wizard_utm("facebook", icp_role, asset_id)
        body = f"Tip voor ZZP — start via Wizard: {utm}"

    try:
        out = comment_on_target(
            tid,
            body,
            mode="mock",
            dry_run=True,
            asset_id=asset_id,
            icp_role=icp_role,
        )
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
            "target_id": tid,
            "live": False,
            "publish": False,
            "marketing": "PARKED_LAST",
        }

    return {
        "ok": bool(out.get("ok")),
        "target_id": tid,
        "result": out,
        "live": False,
        "publish": False,
        "marketing": "PARKED_LAST",
        "desk_status": "SENT" if out.get("ok") else "BLOCK",
    }
