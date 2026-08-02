"""GDrive / Content Factory asset list — OS §E MCP (honest modes).

Modes:
- local_registry: ASSET-REGISTRY.csv (always available, no network)
- stub: LIVE requested but not configured
- not_wired: LIVE+creds but Google Drive folder list API not implemented
Never return fake ok+empty as success.
"""

from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

_REPO = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = _REPO / "docs/ops/demand-os/set-now/ASSET-REGISTRY.csv"


def gdrive_configured() -> bool:
    return bool(
        os.getenv("GDRIVE_FOLDER_ID")
        and (
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            or os.getenv("GA4_CREDENTIALS_JSON")
            or os.getenv("GDRIVE_CREDENTIALS_JSON")
        )
    )


def list_local_registry(*, limit: int = 20, path: Optional[Path] = None) -> Dict[str, Any]:
    src = path or DEFAULT_REGISTRY
    if not src.is_file():
        return {
            "ok": False,
            "mode": "missing_registry",
            "assets": [],
            "error": f"missing {src.name}",
        }
    with src.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assets: List[Dict[str, str]] = []
    for r in rows[: max(1, limit)]:
        assets.append(
            {
                "asset_id": r.get("asset_id") or "",
                "channel": r.get("channel") or "",
                "icp_role": r.get("icp_role") or "",
                "status": r.get("status") or "",
                "source": "ASSET-REGISTRY.csv",
            }
        )
    return {
        "ok": True,
        "mode": "local_registry",
        "assets": assets,
        "error": "",
        "limit": limit,
        "notes": "CF inventory from set-now registry — GDrive folder API separate",
    }


def list_cf_assets(*, limit: int = 5) -> Dict[str, Any]:
    """
    Default: local registry (honest CF list).
    DEMAND_OS_GDRIVE_LIVE=1 → attempt remote; if API missing → not_wired (ok=False).
    """
    if os.getenv("DEMAND_OS_GDRIVE_LIVE") != "1":
        return list_local_registry(limit=limit)

    if not gdrive_configured():
        return {
            "ok": False,
            "mode": "stub",
            "assets": [],
            "error": "DEMAND_OS_GDRIVE_LIVE=1 but missing GDRIVE_FOLDER_ID/creds",
            "limit": limit,
            "fallback": list_local_registry(limit=limit),
        }

    # Honest: folder listing not implemented in agent.media.gdrive (URL normalize only)
    return {
        "ok": False,
        "mode": "not_wired",
        "assets": [],
        "error": "GDrive folder list API not wired — use local_registry",
        "limit": limit,
        "fallback": list_local_registry(limit=limit),
        "notes": "OS §E MCP GDrive = not_wired until Drive list client ships",
    }


def list_cf_assets_stub(*, limit: int = 5) -> Dict[str, Any]:
    """Backward-compatible alias → list_cf_assets."""
    return list_cf_assets(limit=limit)
