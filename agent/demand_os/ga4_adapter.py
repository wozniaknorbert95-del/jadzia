"""GA4 adapter — OS §E MCP (fail-closed; live wrap DTL when env GO).

UTM discipline (Google + industry 2025/26): lowercase source/medium/campaign;
always source+medium+campaign; Demand OS Lock already enforces Wizard template.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List


def ga4_available() -> bool:
    return bool(
        os.getenv("GA4_PROPERTY_ID")
        and (
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            or os.getenv("GA4_CREDENTIALS_JSON")
        )
    )


def fetch_wizard_starts_stub(*, days: int = 7) -> Dict[str, Any]:
    """Alias kept for CLI/tests — routes to fetch_wizard_starts."""
    return fetch_wizard_starts(days=days)


def fetch_wizard_starts(*, days: int = 7) -> Dict[str, Any]:
    """
    Default: fail-closed stub (CI-safe, no network).
    Live: DEMAND_OS_GA4_LIVE=1 + creds → wrap analytics/DTL snapshot (read-only).
    Never invent UTM starts; never claim vanity views as North Star.
    """
    if os.getenv("DEMAND_OS_GA4_LIVE") != "1":
        return {
            "ok": False,
            "mode": "stub",
            "starts": [],
            "error": "GA4 live disabled (set DEMAND_OS_GA4_LIVE=1 + creds)",
            "days": days,
            "utm_policy": "lowercase source/medium/campaign; Wizard Lock template",
        }
    if not ga4_available():
        return {
            "ok": False,
            "mode": "stub",
            "starts": [],
            "error": "missing GA4_PROPERTY_ID or credentials",
            "days": days,
        }

    starts: List[Dict[str, Any]] = []
    try:
        from agent.nodes.analytics_node import fetch_analytics_snapshot

        snapshot = fetch_analytics_snapshot(period_days=days)
        sources = {}
        if snapshot and getattr(snapshot, "sources", None):
            sources = snapshot.sources.model_dump() if hasattr(snapshot.sources, "model_dump") else {}
        # Honest: we do not fabricate per-UTM starts from aggregate snapshots.
        # Surface session totals only as non-North-Star context.
        zz = (sources or {}).get("zzpackage") or {}
        sessions = zz.get("sessions")
        return {
            "ok": True,
            "mode": "live_aggregate",
            "starts": starts,
            "aggregate": {
                "sessions": sessions,
                "sync_status": getattr(snapshot, "sync_status", None),
                "note": "per-UTM starts require GA4 exploration export — not invented here",
            },
            "days": days,
            "error": "",
            "utm_policy": "use Demand OS UTM Lock; ingest via fixture or ops_bus until UTM export wired",
        }
    except Exception as exc:
        return {
            "ok": False,
            "mode": "live_error",
            "starts": [],
            "error": str(exc)[:300],
            "days": days,
        }


def pull_ga4_into_dtl(*, days: int = 7) -> Dict[str, Any]:
    """Optional DTL ingest wrap — only when LIVE=1."""
    if os.getenv("DEMAND_OS_GA4_LIVE") != "1":
        return {
            "ok": False,
            "mode": "stub",
            "error": "DEMAND_OS_GA4_LIVE!=1 — DTL pull skipped",
        }
    try:
        from agent.marketing.dtl.ga4 import ingest_ga4_snapshot

        result = ingest_ga4_snapshot(period_days=days)
        return {"ok": result.get("status") in ("ok", "success", "partial"), "mode": "dtl", "result": result}
    except Exception as exc:
        return {"ok": False, "mode": "dtl_error", "error": str(exc)[:300]}


def fetch_wizard_starts_by_utm(*, days: int = 7) -> Dict[str, Any]:
    """
    Per-UTM starts contract (OS D North Star).
    Default fail-closed — never invent rows.
    When DEMAND_OS_GA4_UTM_CSV is set, parse CSV: utm_link,starts (local export path).
    """
    csv_path = os.getenv("DEMAND_OS_GA4_UTM_CSV", "").strip()
    if not csv_path:
        return {
            "ok": False,
            "mode": "stub",
            "starts_by_utm": {},
            "error": "per-UTM export not configured (set DEMAND_OS_GA4_UTM_CSV or use hub ingest/ops_bus)",
            "days": days,
            "contract": "fail-closed · zero invent",
        }
    from pathlib import Path
    import csv

    path = Path(csv_path)
    if not path.is_file():
        return {
            "ok": False,
            "mode": "missing_file",
            "starts_by_utm": {},
            "error": f"CSV not found: {path}",
            "days": days,
        }
    by_utm: Dict[str, int] = {}
    with path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            utm = (row.get("utm_link") or row.get("utm") or "").strip()
            if not utm:
                continue
            try:
                n = int(row.get("starts") or row.get("wizard_starts") or 0)
            except ValueError:
                n = 0
            if n:
                by_utm[utm] = by_utm.get(utm, 0) + n
    return {
        "ok": True,
        "mode": "utm_csv",
        "starts_by_utm": by_utm,
        "starts": [{"utm_link": k, "starts": v} for k, v in by_utm.items()],
        "days": days,
        "error": "",
        "contract": "import only · never invent",
    }
