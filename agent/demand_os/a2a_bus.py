"""Demand OS A2A bus — OS TARGET §E handoffs (file-backed, no network).

Handoffs: brief_icp · publish_request · engage_event · lead_hot
SLA checked at emit/ack time (minutes).
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

HANDOFF_TYPES = frozenset(
    {
        "brief_icp",
        "publish_request",
        "engage_event",
        "lead_hot",
    }
)

# SLA max minutes (OS §E)
SLA_MINUTES = {
    "brief_icp": 0,  # instant
    "publish_request": 5,
    "engage_event": 15,
    "lead_hot": 15,
}

_DEFAULT_REL = Path("docs/ops/demand-os/set-now/A2A-HANDOFFS.jsonl")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_bus_path() -> Path:
    env = os.environ.get("DEMAND_OS_A2A_BUS")
    if env:
        return Path(env)
    return _repo_root() / _DEFAULT_REL


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def emit_handoff(
    handoff_type: str,
    *,
    payload: Optional[Dict[str, Any]] = None,
    asset_id: Optional[str] = None,
    from_agent: str = "Growth_Lead",
    to_agent: str = "",
    path: Optional[Path] = None,
) -> Dict[str, Any]:
    ht = (handoff_type or "").strip()
    if ht not in HANDOFF_TYPES:
        raise ValueError(f"unknown handoff_type: {ht}")

    routing = {
        "brief_icp": "ICP_Brain",
        "publish_request": "Sniper_Validator",
        "engage_event": "Sales",
        "lead_hot": "CRE_Wizard",
    }
    dest = to_agent or routing[ht]
    now = _utc_now()
    record: Dict[str, Any] = {
        "id": str(uuid4()),
        "ts": now.isoformat(),
        "handoff_type": ht,
        "from_agent": from_agent,
        "to_agent": dest,
        "asset_id": asset_id,
        "payload": payload or {},
        "sla_minutes": SLA_MINUTES[ht],
        "acked_at": None,
        "sla_ok": None,
        "status": "emitted",
    }
    out = path or default_bus_path()
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def ack_handoff(
    handoff_id: str,
    *,
    path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Ack by rewriting JSONL (small file). Marks sla_ok vs emit ts."""
    p = path or default_bus_path()
    if not p.is_file():
        raise KeyError(f"bus empty: {handoff_id}")

    rows: List[Dict[str, Any]] = []
    found: Optional[Dict[str, Any]] = None
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("id") == handoff_id:
            found = row
        rows.append(row)
    if not found:
        raise KeyError(f"handoff not found: {handoff_id}")

    now = _utc_now()
    emitted = _parse_ts(found["ts"])
    elapsed_min = (now - emitted).total_seconds() / 60.0
    sla = float(found.get("sla_minutes") or 0)
    # brief_icp instant: any ack same second is OK; allow 1 min clock skew
    limit = max(sla, 1.0) if sla == 0 else sla
    found["acked_at"] = now.isoformat()
    found["sla_ok"] = elapsed_min <= limit
    found["elapsed_minutes"] = round(elapsed_min, 3)
    found["status"] = "acked"

    with p.open("w", encoding="utf-8") as fh:
        for row in rows:
            if row.get("id") == handoff_id:
                fh.write(json.dumps(found, ensure_ascii=False) + "\n")
            else:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return found


def list_handoffs(
    *,
    path: Optional[Path] = None,
    handoff_type: Optional[str] = None,
    status: Optional[str] = None,
) -> List[Dict[str, Any]]:
    p = path or default_bus_path()
    if not p.is_file():
        return []
    out: List[Dict[str, Any]] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if handoff_type and row.get("handoff_type") != handoff_type:
            continue
        if status and row.get("status") != status:
            continue
        out.append(row)
    return out
