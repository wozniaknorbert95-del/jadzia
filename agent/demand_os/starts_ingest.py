"""Wizard starts / paid ingest — OS TARGET §D · §M (fixture-first, no network in CI)."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent.demand_os.growth_events import append_growth_event, list_growth_events
from agent.demand_os.utm_lock import validate_utm_url

START_EVENT = "wizard_start"
PAID_EVENT = "paid"


def ingest_row(
    *,
    utm_link: str,
    event_type: str = START_EVENT,
    asset_id: Optional[str] = None,
    channel: Optional[str] = None,
    count: int = 1,
    notes: str = "",
    events_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Validate UTM and append wizard_start or paid growth event(s)."""
    et = (event_type or START_EVENT).strip()
    if et not in (START_EVENT, PAID_EVENT):
        raise ValueError(f"event_type must be {START_EVENT!r} or {PAID_EVENT!r}")
    check = validate_utm_url(utm_link)
    if not check.get("ok"):
        raise ValueError(f"bad UTM: {check.get('errors')}")
    parts = check.get("parts") or {}
    ch = channel or parts.get("channel")
    aid = asset_id or parts.get("asset_id")
    n = max(1, int(count))
    last: Dict[str, Any] = {}
    for _ in range(n):
        last = append_growth_event(
            et,
            asset_id=aid,
            channel=ch,
            utm_link=utm_link,
            ok=True,
            notes=notes or f"ingest {et}",
            path=events_path,
        )
    return {"ok": True, "appended": n, "last": last, "utm_parts": parts}


def ingest_fixture_csv(
    path: Path,
    *,
    events_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """CSV columns: utm_link,event_type,asset_id,channel,count,notes"""
    if not path.is_file():
        raise FileNotFoundError(str(path))
    rows_ok = 0
    errors: List[str] = []
    with path.open(encoding="utf-8", newline="") as fh:
        for i, row in enumerate(csv.DictReader(fh), start=2):
            utm = (row.get("utm_link") or "").strip()
            if not utm:
                errors.append(f"line {i}: missing utm_link")
                continue
            try:
                ingest_row(
                    utm_link=utm,
                    event_type=(row.get("event_type") or START_EVENT).strip(),
                    asset_id=(row.get("asset_id") or "").strip() or None,
                    channel=(row.get("channel") or "").strip() or None,
                    count=int(row.get("count") or 1),
                    notes=(row.get("notes") or "").strip(),
                    events_path=events_path,
                )
                rows_ok += 1
            except (ValueError, TypeError) as exc:
                errors.append(f"line {i}: {exc}")
    return {"ok": not errors, "rows_ok": rows_ok, "errors": errors}


def aggregate_starts_from_events(
    *,
    events_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Aggregate wizard_start / paid from growth_events JSONL."""
    events = list_growth_events(path=events_path, limit=0)
    starts_by: Dict[str, int] = {}
    paid_total = 0
    hook_scores: Dict[str, int] = {}
    for e in events:
        et = e.get("event_type")
        utm = (e.get("utm_link") or "").strip()
        asset = (e.get("asset_id") or "").strip() or "unknown"
        if et == START_EVENT and utm:
            starts_by[utm] = starts_by.get(utm, 0) + 1
            hook_scores[asset] = hook_scores.get(asset, 0) + 1
        elif et == PAID_EVENT:
            paid_total += 1
            if asset:
                hook_scores[asset] = hook_scores.get(asset, 0)
    top_hook = ""
    if hook_scores:
        top_hook = max(hook_scores.items(), key=lambda kv: kv[1])[0]
    return {
        "starts_by_utm": starts_by,
        "starts_utm": sum(starts_by.values()),
        "paid": paid_total,
        "top_hook": top_hook,
    }


def write_sample_fixture(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "utm_link,event_type,asset_id,channel,count,notes\n"
        "https://zzpackage.flexgrafik.nl/wizard/?utm_source=tiktok&utm_medium=organic"
        "&utm_campaign=icp_installateur&utm_content=tt_w32_install_01,"
        "wizard_start,tt_w32_install_01,tiktok,2,fixture\n"
        "https://zzpackage.flexgrafik.nl/wizard/?utm_source=facebook&utm_medium=organic"
        "&utm_campaign=icp_installateur&utm_content=fb_hunt_w32_d2,"
        "wizard_start,fb_hunt_w32_d2,facebook,1,fixture\n"
        "https://zzpackage.flexgrafik.nl/wizard/?utm_source=tiktok&utm_medium=organic"
        "&utm_campaign=icp_installateur&utm_content=tt_w32_install_01,"
        "paid,tt_w32_install_01,tiktok,1,fixture paid\n",
        encoding="utf-8",
    )
    return path
