"""Content Factory brief builder — OS §H CF (local assets, no GDrive required)."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent.demand_os.memory import load_memory
from agent.demand_os.utm_lock import build_wizard_utm

_REPO = Path(__file__).resolve().parents[2]
ASSET_REG = _REPO / "docs/ops/demand-os/set-now/ASSET-REGISTRY.csv"
PROOF_TIER0 = frozenset({"hq", "vhq", "dashboard", "agent_os", "mission_control"})


def _icp_hook() -> Dict[str, str]:
    mem = load_memory()
    sem = (mem.get("semantic") or {}) if isinstance(mem, dict) else {}
    return {
        "role": str(
            sem.get("icp_role_week") or sem.get("icp_role") or "installateur"
        ),
        "hook": str(
            sem.get("hook_nl")
            or sem.get("hook")
            or "witte bus · opdrachtgever ziet je niet"
        ),
    }


def list_local_assets(*, limit: int = 20) -> List[Dict[str, str]]:
    if not ASSET_REG.is_file():
        return []
    with ASSET_REG.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    return rows[:limit]


def build_brief(
    *,
    channel: str = "tiktok",
    asset_id: Optional[str] = None,
    proof_tier: int = 1,
) -> Dict[str, Any]:
    """One ICP · one CTA · proof tier ≥1 (tier 0 = HQ = FAIL)."""
    icp = _icp_hook()
    aid = asset_id or f"{channel[:2]}_w_auto_01"
    if proof_tier <= 0:
        return {
            "ok": False,
            "error": "proof_tier_0_forbidden",
            "notes": "OS B.8 — HQ/VHQ screenshot never as hero",
        }
    utm = build_wizard_utm(channel, icp["role"], aid)
    assets = list_local_assets(limit=10)
    return {
        "ok": True,
        "brief": {
            "icp_role": icp["role"],
            "hook": icp["hook"],
            "channel": channel,
            "asset_id": aid,
            "cta": "1 Wizard UTM only",
            "utm_link": utm,
            "proof_tier": proof_tier,
            "proof_hint": "prefer real bus B/A or Google review — never HQ",
            "local_assets_sample": assets[:3],
        },
        "marketing": "PARKED_LAST",
        "live_publish": False,
    }


def proof_check(label: str) -> Dict[str, Any]:
    low = (label or "").strip().lower()
    bad = any(t in low for t in PROOF_TIER0)
    return {
        "ok": not bad,
        "tier": 0 if bad else 1,
        "label": label,
        "rule": "B.8 proof hierarchy — tier0=HQ forbidden",
    }
