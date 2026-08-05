"""Agent heartbeat — last_run tracking per registry role (file-backed, no network).

Registry roles are orchestration shells; heartbeat records when a role actually
ran so `list_agents()` can show recency instead of a static declaration.
Honesty: heartbeat proves a run happened, not that live cadence PASSed.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

_REPO = Path(__file__).resolve().parents[3]
_DEFAULT_REL = Path("docs/ops/demand-os/set-now/AGENTS-HEARTBEAT.json")
STALE_DAYS = 7

# Per-role staleness policy for worker-supervised (cadence) roles — single
# source of truth shared by heartbeat_view (desk chip) and wave_check
# (readiness gate). Values = 2x worker CADENCE (drift margin).
STALE_LIMITS_H: Dict[str, float] = {
    "growth_lead": 48.0,
    "sales": 12.0,
    "validator": 48.0,
    "icp_brain": 48.0,
    "cre": 48.0,
}


def stale_limit_hours(role: str, *, default_h: float) -> float:
    """Single staleness policy: env override > per-role table > caller default.

    Env override DEMAND_OS_HB_STALE_<ROLE> (hours) wins; then the per-role
    table; then the caller's default (wave_check: 48h, desk view: STALE_DAYS).
    """
    env = os.environ.get(f"DEMAND_OS_HB_STALE_{(role or '').strip().upper()}")
    if env:
        return float(env)
    return float(STALE_LIMITS_H.get(role, default_h))


def default_heartbeat_path() -> Path:
    """Resolve heartbeat path via the shared writable-path contract."""
    from agent.demand_os.state_paths import resolve_writable_path

    return resolve_writable_path(_DEFAULT_REL.name, env_var="DEMAND_OS_AGENTS_HEARTBEAT")


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
    limit_h = stale_limit_hours(role, default_h=STALE_DAYS * 24.0)
    return {
        "last_run_at": rec.get("last_run_at"),
        "last_action": rec.get("last_action"),
        "run_count": rec.get("run_count") or 0,
        "age_days": age,
        "stale": (age is None) or age * 24.0 > limit_h,
        "stale_limit_h": limit_h,
    }
