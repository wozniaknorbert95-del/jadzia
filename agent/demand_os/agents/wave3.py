"""Wave3 shells — Blog ICP + CRE Wizard (OS §J). Live ship stays false until unlock."""

from __future__ import annotations

from typing import Any, Dict

from agent.demand_os.blog_pipeline import list_drafts, run_pipeline
from agent.demand_os.marketing_mode import resolve_marketing_mode
from agent.demand_os.utm_lock import build_wizard_utm
from agent.demand_os.widget_leads import list_hot_leads

WAVE3_ROLES = frozenset({"blog", "cre"})


def _mode() -> str:
    return resolve_marketing_mode()


def run_wave3(role: str, *, action: str = "status", **kwargs: Any) -> Dict[str, Any]:
    r = (role or "").strip().lower()
    if r not in WAVE3_ROLES:
        raise ValueError(f"wave3 role must be blog|cre, got {role}")
    if r == "blog":
        return _blog(action, **kwargs)
    return _cre(action, **kwargs)


def _blog(action: str, **kwargs: Any) -> Dict[str, Any]:
    act = (action or "status").strip().lower()
    icp = str(kwargs.get("icp_role") or "installateur")
    if act in ("pipeline", "generate", "run"):
        result = run_pipeline(
            icp,
            asset_id=kwargs.get("asset_id"),
            angle=kwargs.get("angle"),
            persist=bool(kwargs.get("persist", True)),
            calendar=bool(kwargs.get("calendar", True)),
            log=True,
            emit_events=False,
        )
        return {
            "role": "blog",
            "action": act,
            "result": result,
            "live_ship": False,
            "kpi": "organic→starts",
            "marketing": _mode(),
            "wave": 3,
        }
    drafts = list_drafts()
    utm = build_wizard_utm("blog", icp, "blog_w_icp_01")
    return {
        "role": "blog",
        "action": "status",
        "result": {
            "cadence": "1 / week",
            "icp_role": icp,
            "cta": "Wizard UTM blog only",
            "utm_link": utm,
            "drafts": [
                d.get("asset_id") or d.get("slug") or str(d)[:80] for d in drafts[:10]
            ],
            "draft_count": len(drafts),
            "live_ship": False,
            "actions": ["status", "pipeline"],
            "cli": "tools/demand_os_f4.py · agents --role blog --action pipeline",
        },
        "kpi": "organic→starts",
        "marketing": _mode(),
        "wave": 3,
    }


def _cre(action: str, **kwargs: Any) -> Dict[str, Any]:
    hot = list_hot_leads(limit=int(kwargs.get("limit") or 5))
    return {
        "role": "cre",
        "action": action or "status",
        "result": {
            "job": "Wizard session path — no offerte-as-success",
            "hot_leads": hot.get("leads") or [],
            "deeplink_rule": "every design lead → Wizard <24h",
            "cli": "hub design-check",
        },
        "kpi": "Wizard starts from hot",
        "marketing": _mode(),
        "wave": 3,
    }
