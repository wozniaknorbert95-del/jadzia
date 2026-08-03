"""Wave2 agent shells — CF + FB (OS §J). Live engage stays false until unlock."""

from __future__ import annotations

from typing import Any, Dict

from agent.demand_os.connectors.allowlist import load_allowlist
from agent.demand_os.content_factory import build_brief, list_local_assets, proof_check
from agent.demand_os.gdrive_cf import list_cf_assets_stub
from agent.demand_os.marketing_mode import resolve_marketing_mode

WAVE2_ROLES = frozenset({"cf", "fb", "content_factory", "agent_fb"})


def _mode() -> str:
    return resolve_marketing_mode()


def run_wave2(role: str, *, action: str = "status", **kwargs: Any) -> Dict[str, Any]:
    r = (role or "").strip().lower()
    if r in ("content_factory",):
        r = "cf"
    if r in ("agent_fb",):
        r = "fb"
    if r not in ("cf", "fb"):
        raise ValueError(f"wave2 role must be cf|fb, got {role}")
    act = (action or "status").strip().lower()
    if r == "cf":
        return _cf(act, **kwargs)
    return _fb(act, **kwargs)


def _cf(action: str, **kwargs: Any) -> Dict[str, Any]:
    if action == "brief":
        return {
            "role": "cf",
            "action": action,
            "result": build_brief(
                channel=str(kwargs.get("channel") or "tiktok"),
                asset_id=kwargs.get("asset_id"),
                proof_tier=int(kwargs.get("proof_tier") or 1),
            ),
            "marketing": _mode(),
        }
    if action == "assets":
        return {
            "role": "cf",
            "action": action,
            "result": {
                "local": list_local_assets(limit=int(kwargs.get("limit") or 10)),
                "gdrive": list_cf_assets_stub(limit=5),
            },
            "marketing": _mode(),
        }
    if action == "proof":
        return {
            "role": "cf",
            "action": action,
            "result": proof_check(str(kwargs.get("label") or "")),
            "marketing": _mode(),
        }
    return {
        "role": "cf",
        "action": "status",
        "result": build_brief(channel="tiktok"),
        "kpi": "assets with 1 CTA · proof≥1",
        "marketing": _mode(),
        "wave": 2,
        "note": "Wave2 shell — live ship gated by Dowódca unlock",
    }


def _fb(action: str, **kwargs: Any) -> Dict[str, Any]:
    al = load_allowlist()
    targets = [
        {
            "id": t.id,
            "name": t.name,
            "status": t.status,
            "engageable": t.is_engageable,
            "kind": t.kind,
        }
        for t in al.get("targets") or []
    ]
    engageable = [t for t in targets if t["engageable"]]
    return {
        "role": "fb",
        "action": action or "allowlist",
        "result": {
            "targets": targets,
            "engageable_count": len(engageable),
            "max_groups": al.get("max_groups"),
            "live_comment": False,
            "note": "live_comment=false until Dowódca unlock after tool 100%",
        },
        "kpi": "starts facebook + qualified comments/day",
        "marketing": _mode(),
        "wave": 2,
    }
