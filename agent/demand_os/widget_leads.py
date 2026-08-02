"""Widget/leads → A2A Sales handoff — OS §E MCP (DB read when available)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from agent.demand_os.a2a_bus import emit_handoff
from agent.demand_os.utm_lock import build_wizard_utm

HOT_SCORE = 80


def emit_hot_lead(
    *,
    lead_id: str,
    asset_id: Optional[str] = None,
    wizard_url: str = "",
    notes: str = "",
    bus_path=None,
) -> Dict[str, Any]:
    """Emit lead_hot handoff (STL path). No network."""
    return emit_handoff(
        "lead_hot",
        asset_id=asset_id or lead_id,
        from_agent="Sales",
        to_agent="CRE_Wizard",
        payload={
            "lead_id": lead_id,
            "wizard_url": wizard_url,
            "notes": notes,
        },
        path=bus_path,
    )


def emit_engage_to_sales(
    *,
    target_id: str,
    asset_id: str,
    utm_link: str = "",
    bus_path=None,
) -> Dict[str, Any]:
    return emit_handoff(
        "engage_event",
        asset_id=asset_id,
        from_agent="Agent_FB",
        to_agent="Sales",
        payload={"target_id": target_id, "utm_link": utm_link},
        path=bus_path,
    )


def list_hot_leads(*, limit: int = 20) -> Dict[str, Any]:
    """List open hot leads from jadzia.db; stub empty if DB unavailable."""
    try:
        from agent.db import db_list_leads

        rows = db_list_leads(limit=max(limit, 50))
    except Exception as exc:
        return {
            "ok": False,
            "mode": "stub",
            "leads": [],
            "error": str(exc)[:200],
            "notes": "DB unavailable — use emit_hot_lead manually",
        }

    hot: List[Dict[str, Any]] = []
    for lead in rows:
        if lead.get("is_test") is True:
            continue
        if (lead.get("disposition") or "open").lower() in ("closed", "snoozed"):
            continue
        score = int(lead.get("game_score") or 0)
        if score < HOT_SCORE:
            continue
        lid = str(lead.get("id"))
        hot.append(
            {
                "lead_id": lid,
                "email": lead.get("email") or "",
                "game_score": score,
                "source": lead.get("source") or "",
                "wizard_url": build_wizard_utm(
                    "whatsapp", "installateur", f"lead_{lid}"
                ),
            }
        )
        if len(hot) >= limit:
            break

    return {
        "ok": True,
        "mode": "jadzia.db",
        "leads": hot,
        "notes": "hot = game_score>=80 open non-test",
    }


def sync_hot_leads_to_a2a(
    *,
    limit: int = 10,
    bus_path=None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Emit lead_hot for each hot lead (STL path). dry_run = list only."""
    listed = list_hot_leads(limit=limit)
    if not listed.get("ok"):
        return listed
    emitted = []
    for lead in listed.get("leads") or []:
        if dry_run:
            emitted.append({"lead_id": lead["lead_id"], "dry_run": True})
            continue
        rec = emit_hot_lead(
            lead_id=lead["lead_id"],
            wizard_url=lead.get("wizard_url") or "",
            notes=f"score={lead.get('game_score')} source={lead.get('source')}",
            bus_path=bus_path,
        )
        emitted.append({"lead_id": lead["lead_id"], "handoff_id": rec.get("id")})
    return {
        "ok": True,
        "mode": listed.get("mode"),
        "emitted": len(emitted),
        "items": emitted,
        "dry_run": dry_run,
        "marketing": "PARKED_LAST",
    }


def list_hot_leads_stub() -> Dict[str, Any]:
    """Backward-compatible alias."""
    return list_hot_leads(limit=5)
