"""jadzia.db / ops_bus → Demand OS North Star wire (OS §E MCP jadzia.db+UTM).

Syncs ops_bus `wizard_started` into growth_events. Fail-closed without DB.
No network. No invent starts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent.demand_os.starts_ingest import ingest_row
from agent.demand_os.utm_lock import build_wizard_utm, validate_utm_url


def sync_wizard_starts_from_ops_bus(
    *,
    limit: int = 50,
    events_path: Optional[Path] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Read ops_bus wizard_started rows → append wizard_start growth events.
    UTM: from payload if valid Lock form; else rebuild from source/medium/content.
    """
    try:
        from agent.db import db_ops_bus_list
    except Exception as exc:
        return {"ok": False, "mode": "no_db", "synced": 0, "error": str(exc)[:200]}

    try:
        rows = db_ops_bus_list(event_type="wizard_started", limit=limit) or []
    except Exception as exc:
        return {"ok": False, "mode": "db_error", "synced": 0, "error": str(exc)[:200]}

    synced = 0
    skipped = 0
    errors: List[str] = []
    details: List[Dict[str, Any]] = []

    for row in rows:
        payload = row.get("payload") or row.get("payload_json") or {}
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                payload = {}
        utm = (payload.get("utm_link") or payload.get("url") or "").strip()
        asset_id = (
            payload.get("asset_id")
            or payload.get("utm_content")
            or row.get("source_event_id")
            or f"ops_{row.get('id') or row.get('event_id') or 'x'}"
        )
        channel = (payload.get("utm_source") or payload.get("channel") or "tiktok").strip()
        role = (payload.get("icp_role") or "installateur").strip()

        if utm:
            check = validate_utm_url(utm)
            if not check.get("ok"):
                try:
                    utm = build_wizard_utm(
                        channel if channel in ("tiktok", "facebook", "blog", "whatsapp") else "tiktok",
                        role,
                        str(asset_id),
                    )
                except Exception as exc:
                    skipped += 1
                    errors.append(f"utm rebuild fail: {exc}")
                    continue
        else:
            try:
                utm = build_wizard_utm(
                    channel if channel in ("tiktok", "facebook", "blog", "whatsapp") else "tiktok",
                    role,
                    str(asset_id),
                )
            except Exception as exc:
                skipped += 1
                errors.append(str(exc)[:120])
                continue

        if dry_run:
            details.append({"asset_id": asset_id, "utm_link": utm, "dry_run": True})
            synced += 1
            continue
        try:
            ingest_row(
                utm_link=utm,
                event_type="wizard_start",
                asset_id=str(asset_id),
                channel=channel if channel in ("tiktok", "facebook", "blog", "whatsapp") else None,
                notes=f"ops_bus wizard_started id={row.get('event_id') or row.get('id')}",
                events_path=events_path,
            )
            synced += 1
            details.append({"asset_id": asset_id, "utm_link": utm, "ok": True})
        except ValueError as exc:
            skipped += 1
            errors.append(str(exc)[:120])

    return {
        "ok": True,
        "mode": "ops_bus",
        "synced": synced,
        "skipped": skipped,
        "errors": errors[:20],
        "details": details[:20],
        "dry_run": dry_run,
    }


def sync_paid_from_ops_bus(
    *,
    limit: int = 50,
    events_path: Optional[Path] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """ops_bus order_created → growth_events paid (no invent UTM)."""
    try:
        from agent.db import db_ops_bus_list
    except Exception as exc:
        return {"ok": False, "mode": "no_db", "synced": 0, "error": str(exc)[:200]}

    try:
        rows = db_ops_bus_list(event_type="order_created", limit=limit) or []
    except Exception as exc:
        return {"ok": False, "mode": "db_error", "synced": 0, "error": str(exc)[:200]}

    synced = 0
    skipped = 0
    errors: List[str] = []
    details: List[Dict[str, Any]] = []

    for row in rows:
        payload = row.get("payload") or row.get("payload_json") or {}
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                payload = {}
        utm = (payload.get("utm_link") or payload.get("utm") or "").strip()
        asset_id = (
            payload.get("asset_id")
            or payload.get("utm_content")
            or f"order_{row.get('id') or row.get('event_id') or 'x'}"
        )
        channel = (payload.get("utm_source") or payload.get("channel") or "tiktok").strip()
        if not utm:
            try:
                utm = build_wizard_utm(
                    channel if channel in ("tiktok", "facebook", "blog", "whatsapp", "design_agent") else "tiktok",
                    (payload.get("icp_role") or "installateur").strip(),
                    str(asset_id),
                )
            except Exception as exc:
                skipped += 1
                errors.append(str(exc)[:120])
                continue
        else:
            check = validate_utm_url(utm)
            if not check.get("ok"):
                skipped += 1
                errors.append(f"utm invalid order {asset_id}")
                continue

        if dry_run:
            details.append({"asset_id": asset_id, "utm_link": utm, "dry_run": True})
            synced += 1
            continue
        try:
            ingest_row(
                utm_link=utm,
                event_type="paid",
                asset_id=str(asset_id),
                channel=channel if channel in ("tiktok", "facebook", "blog", "whatsapp", "design_agent") else None,
                notes=f"ops_bus order_created id={row.get('event_id') or row.get('id')}",
                events_path=events_path,
            )
            synced += 1
            details.append({"asset_id": asset_id, "ok": True})
        except ValueError as exc:
            skipped += 1
            errors.append(str(exc)[:120])

    return {
        "ok": True,
        "mode": "ops_bus_paid",
        "synced": synced,
        "skipped": skipped,
        "errors": errors[:20],
        "details": details[:20],
        "dry_run": dry_run,
    }
