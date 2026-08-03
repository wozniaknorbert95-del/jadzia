"""Append-only growth_events log (Demand OS F1).

File-backed JSONL so F1 works without VPS schema deploy.
Default path: docs/ops/demand-os/set-now/GROWTH-EVENTS.jsonl
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from uuid import uuid4

EVENT_TYPES = frozenset(
    {
        "cta_issued",
        "cta_validated",
        "cta_rejected",
        "publish_frozen",
        "bridge_proof",
        "wizard_start",
        "paid",
    }
)

_DEFAULT_REL = Path("docs/ops/demand-os/set-now/GROWTH-EVENTS.jsonl")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_events_path() -> Path:
    from agent.demand_os.state_paths import resolve_writable_path

    return resolve_writable_path(_DEFAULT_REL.name, env_var="DEMAND_OS_GROWTH_EVENTS")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def append_growth_event(
    event_type: str,
    *,
    asset_id: Optional[str] = None,
    channel: Optional[str] = None,
    utm_link: Optional[str] = None,
    ok: Optional[bool] = None,
    errors: Optional[Iterable[str]] = None,
    notes: str = "",
    path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Append one growth event; returns the written record."""
    et = (event_type or "").strip()
    if et not in EVENT_TYPES:
        raise ValueError(f"unknown event_type: {et}")

    record: Dict[str, Any] = {
        "id": str(uuid4()),
        "ts": _utc_now(),
        "event_type": et,
        "asset_id": asset_id,
        "channel": channel,
        "utm_link": utm_link,
        "ok": ok,
        "errors": list(errors or []),
        "notes": notes or "",
    }
    out = path or default_events_path()
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def list_growth_events(
    *,
    path: Optional[Path] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Return last `limit` events (newest last)."""
    src = path or default_events_path()
    if not src.is_file():
        return []
    rows: List[Dict[str, Any]] = []
    with src.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    if limit <= 0:
        return rows
    return rows[-limit:]
