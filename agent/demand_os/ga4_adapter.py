"""GA4 adapter — OS §E MCP (fail-closed; live wrap DTL when env GO).

UTM discipline (Google + industry 2025/26): lowercase source/medium/campaign;
always source+medium+campaign; Demand OS Lock already enforces Wizard template.

Honesty contract:
- stub / missing creds / API error → status unavailable (never invent zero as success)
- sessions ≠ wizard starts ≠ UTM-attributed starts
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def ga4_available() -> bool:
    """True when credentials and a zzpackage/app/legacy property id exist."""
    creds = (
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
        or os.getenv("GA4_CREDENTIALS_JSON", "").strip()
    )
    if not creds:
        return False
    return bool(
        os.getenv("GA4_PROPERTY_ID_ZZPACKAGE", "").strip()
        or os.getenv("GA4_PROPERTY_ID_APP", "").strip()
        or os.getenv("GA4_PROPERTY_ID", "").strip()
    )


def _unavailable(
    *,
    mode: str,
    reason: str,
    days: int,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "ok": False,
        "status": "unavailable",
        "mode": mode,
        "starts": [],
        "ga4_sessions_7d": None,
        "ga4_wizard_starts_7d": None,
        "error": reason,
        "reason": reason,
        "days": days,
        "freshness": None,
        "utm_policy": "lowercase source/medium/campaign; Wizard Lock template",
        "contract": "fail-closed · zero invent · sessions ≠ starts",
    }
    if extra:
        out.update(extra)
    return out


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
        return _unavailable(
            mode="stub",
            reason="GA4 live disabled (set DEMAND_OS_GA4_LIVE=1 + creds)",
            days=days,
        )
    if not ga4_available():
        return _unavailable(
            mode="missing_config",
            reason="missing GA4 property id or credentials",
            days=days,
        )

    starts: List[Dict[str, Any]] = []
    try:
        from agent.nodes.analytics_node import fetch_analytics_snapshot

        snapshot = fetch_analytics_snapshot(period_days=days)
        sources = {}
        if snapshot and getattr(snapshot, "sources", None):
            sources = (
                snapshot.sources.model_dump()
                if hasattr(snapshot.sources, "model_dump")
                else {}
            )
        zz = (sources or {}).get("zzpackage") or {}
        sessions = zz.get("sessions")
        # Optional configured event name for wizard start (projection only).
        event_name = os.getenv("DEMAND_OS_GA4_WIZARD_START_EVENT", "").strip()
        wizard_starts: Optional[int] = None
        if event_name and isinstance(zz.get("events"), dict):
            try:
                wizard_starts = int(zz["events"].get(event_name) or 0)
            except (TypeError, ValueError):
                wizard_starts = None

        freshness = None
        sync_status = getattr(snapshot, "sync_status", None)
        fetched_at = getattr(snapshot, "fetched_at", None) or getattr(
            snapshot, "created_at", None
        )
        if fetched_at is not None:
            freshness = str(fetched_at)
        elif sync_status:
            freshness = str(sync_status)

        return {
            "ok": True,
            "status": "ok",
            "mode": "live_aggregate",
            "starts": starts,
            "ga4_sessions_7d": sessions,
            "ga4_wizard_starts_7d": wizard_starts,
            "aggregate": {
                "sessions": sessions,
                "wizard_starts_event": event_name or None,
                "wizard_starts": wizard_starts,
                "sync_status": sync_status,
                "note": "per-UTM starts require GA4 exploration export — not invented here",
            },
            "days": days,
            "freshness": freshness or datetime.now(timezone.utc).isoformat(),
            "error": "",
            "reason": "",
            "utm_policy": "use Demand OS UTM Lock; ingest via fixture or ops_bus until UTM export wired",
            "contract": "fail-closed · zero invent · sessions ≠ starts",
        }
    except Exception as exc:
        return _unavailable(
            mode="live_error",
            reason=str(exc)[:300],
            days=days,
        )


def pull_ga4_into_dtl(*, days: int = 7) -> Dict[str, Any]:
    """Optional DTL ingest wrap — only when LIVE=1."""
    if os.getenv("DEMAND_OS_GA4_LIVE") != "1":
        return {
            "ok": False,
            "mode": "stub",
            "status": "unavailable",
            "error": "DEMAND_OS_GA4_LIVE!=1 — DTL pull skipped",
        }
    try:
        from agent.marketing.dtl.ga4 import ingest_ga4_snapshot

        result = ingest_ga4_snapshot(period_days=days)
        return {
            "ok": result.get("status") in ("ok", "success", "partial"),
            "mode": "dtl",
            "status": "ok" if result.get("status") in ("ok", "success", "partial") else "unavailable",
            "result": result,
        }
    except Exception as exc:
        return {"ok": False, "mode": "dtl_error", "status": "unavailable", "error": str(exc)[:300]}


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
            "status": "unavailable",
            "mode": "stub",
            "starts_by_utm": {},
            "error": "per-UTM export not configured (set DEMAND_OS_GA4_UTM_CSV or use hub ingest/ops_bus)",
            "reason": "per-UTM export not configured",
            "days": days,
            "contract": "fail-closed · zero invent",
        }
    from pathlib import Path
    import csv

    path = Path(csv_path)
    if not path.is_file():
        return {
            "ok": False,
            "status": "unavailable",
            "mode": "missing_file",
            "starts_by_utm": {},
            "error": f"CSV not found: {path}",
            "reason": f"CSV not found: {path}",
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
        "status": "ok",
        "mode": "utm_csv",
        "starts_by_utm": by_utm,
        "starts": [{"utm_link": k, "starts": v} for k, v in by_utm.items()],
        "days": days,
        "error": "",
        "reason": "",
        "contract": "import only · never invent",
    }
