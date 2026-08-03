"""Agent heartbeat — last_run tracking per registry role (file-backed, no network).

Registry roles are orchestration shells; heartbeat records when a role actually
ran so `list_agents()` can show recency instead of a static declaration.
Honesty: heartbeat proves a run happened, not that live cadence PASSed.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

_REPO = Path(__file__).resolve().parents[3]
_DEFAULT_REL = Path("docs/ops/demand-os/set-now/AGENTS-HEARTBEAT.json")
STALE_DAYS = 7


def default_heartbeat_path() -> Path:
    env = os.environ.get("DEMAND_OS_AGENTS_HEARTBEAT")
    if env:
        return Path(env)
    return _REPO / _DEFAULT_REL


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_heartbeats(*, path: Optional[Path] = None) -> Dict[str, Any]:
    p = path or default_heartbeat_path()
    if not p.is_file():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def record_heartbeat(
    role: str,
    *,
    action: str = "status",
    path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Upsert role heartbeat. Returns the stored record."""
    from agent.demand_os.agents.registry import get_agent

    r = (role or "").strip().lower()
    if get_agent(r) is None:
        raise ValueError(f"unknown role {role!r}")
    p = path or default_heartbeat_path()
    data = load_heartbeats(path=p)
    prev = data.get(r) or {}
    rec = {
        "role": r,
        "last_run_at": _utc_now_iso(),
        "last_action": (action or "status").strip().lower(),
        "run_count": int(prev.get("run_count") or 0) + 1,
    }
    data[r] = rec
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(p)
    return rec


def heartbeat_age_days(rec: Dict[str, Any]) -> Optional[float]:
    ts = rec.get("last_run_at")
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except ValueError:
        return None
    return round((datetime.now(timezone.utc) - dt).total_seconds() / 86400.0, 2)


def heartbeat_view(role: str, *, path: Optional[Path] = None) -> Dict[str, Any]:
    rec = load_heartbeats(path=path).get(role) or {}
    age = heartbeat_age_days(rec) if rec else None
    return {
        "last_run_at": rec.get("last_run_at"),
        "last_action": rec.get("last_action"),
        "run_count": rec.get("run_count") or 0,
        "age_days": age,
        "stale": (age is None) or age > STALE_DAYS,
    }
