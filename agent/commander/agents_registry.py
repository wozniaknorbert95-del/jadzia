"""Agent registry with SLA status."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from agent.commander.sla import _parse_ts, dtl_ingest_fetched_at
from agent.db import (
    db_commander_get_agent_state,
    db_commander_list_agent_states,
    db_commander_upsert_agent_state,
    db_count_calendar_by_status,
    db_list_calendar_entries,
)

logger = logging.getLogger(__name__)

DEFAULT_AGENTS = [
    {"agent_id": "marketing", "label": "Marketing / FB", "expected_interval_seconds": 3600},
    {"agent_id": "marketing_brain", "label": "Marketing Brain (MB)", "expected_interval_seconds": 3600},
    {"agent_id": "analytics", "label": "Analytics GA4", "expected_interval_seconds": 7200},
    {"agent_id": "sales", "label": "Sales / Leads", "expected_interval_seconds": 1800},
    {"agent_id": "operations", "label": "Operations / Orders", "expected_interval_seconds": 1800},
    {"agent_id": "design", "label": "Design INSPIRE", "expected_interval_seconds": 86400},
]

# Pipeline agents: durable clock = DTL raw ingest (same SoT as Ops freshness).
AGENT_DTL_CLOCK = {
    "analytics": "ga4",
    "sales": "leads",
    "operations": "orders",
}

# HITL / on-demand — no scheduled heartbeat. Missing last_run is n/a, not breach.
SLA_UNTRACKED_WITHOUT_RUN = frozenset({"marketing", "design"})


def _ensure_defaults() -> None:
    for spec in DEFAULT_AGENTS:
        if not db_commander_get_agent_state(spec["agent_id"]):
            db_commander_upsert_agent_state(spec["agent_id"], {
                "status": "LIVE",
                "expected_interval_seconds": spec["expected_interval_seconds"],
                "held_count": 0,
            })


def _sla_ok(last_run_at: Optional[str], interval_s: int) -> bool:
    dt = _parse_ts(last_run_at)
    if not dt:
        return False
    age = (datetime.now(timezone.utc) - dt).total_seconds()
    return age <= interval_s * 2


def _next_expected_run(last_run_at: Optional[str], interval_s: int) -> Optional[str]:
    """ISO-8601 UTC for last_run + interval; None if unknown."""
    dt = _parse_ts(last_run_at)
    if not dt or not interval_s or interval_s <= 0:
        return None
    nxt = datetime.fromtimestamp(dt.timestamp() + int(interval_s), tz=timezone.utc)
    return nxt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _effective_last_run(agent_id: str, stored: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """Return (last_run_at, clock_source). Pipeline agents: newer of agent_state vs DTL."""
    dtl_source = AGENT_DTL_CLOCK.get(agent_id)
    dtl = dtl_ingest_fetched_at(dtl_source) if dtl_source else None
    if stored and dtl:
        st = _parse_ts(stored)
        dt = _parse_ts(dtl)
        if st and dt:
            if dt >= st:
                return dtl, f"dtl:{dtl_source}"
            return stored, "agent_state"
        if dt:
            return dtl, f"dtl:{dtl_source}"
        return stored, "agent_state"
    if stored:
        return stored, "agent_state"
    if dtl:
        return dtl, f"dtl:{dtl_source}"
    return None, None


def _compute_sla_ok(agent_id: str, last_run_at: Optional[str], interval_s: int) -> Optional[bool]:
    """
    True/False when agent is on a scheduled clock.
    None = HITL/on-demand (marketing publish, design) — not a Start 'SLA bad' signal.
    Stale HITL last_run must not scream breach (organic is human-paced).
    """
    if agent_id in SLA_UNTRACKED_WITHOUT_RUN:
        return None
    if last_run_at:
        return _sla_ok(last_run_at, interval_s)
    return False


def list_agents() -> List[Dict]:
    _ensure_defaults()
    states = {r["agent_id"]: r for r in db_commander_list_agent_states()}
    out = []
    for spec in DEFAULT_AGENTS:
        row = states.get(spec["agent_id"], {})
        interval = row.get("expected_interval_seconds") or spec["expected_interval_seconds"]
        last_run, clock_source = _effective_last_run(spec["agent_id"], row.get("last_run_at"))
        held = row.get("held_count") or 0
        if spec["agent_id"] == "marketing":
            held = db_count_calendar_by_status("held")
        out.append({
            "agent_id": spec["agent_id"],
            "label": spec["label"],
            "status": row.get("status", "LIVE"),
            "last_run_at": last_run,
            "last_error": row.get("last_error"),
            "expected_interval_seconds": interval,
            "sla_ok": _compute_sla_ok(spec["agent_id"], last_run, interval),
            "held_count": held,
            "next_expected_run": _next_expected_run(last_run, interval),
            "clock_source": clock_source,
        })
    return out


def pause_agent(agent_id: str) -> Dict:
    held = 0
    if agent_id == "marketing":
        from agent.db import db_update_calendar_entry

        for status in ("approved", "pending_approval"):
            entries = db_list_calendar_entries(status=status, limit=200)
            for entry in entries:
                db_update_calendar_entry(int(entry["entry_id"]), {"status": "held"})
                held += 1
    db_commander_upsert_agent_state(agent_id, {"status": "PAUSED", "held_count": held})
    return {"agent_id": agent_id, "status": "PAUSED", "held_count": held}


def resume_agent(agent_id: str) -> Dict:
    released = 0
    if agent_id == "marketing":
        entries = db_list_calendar_entries(status="held", limit=200)
        from agent.db import db_update_calendar_entry

        for entry in entries:
            db_update_calendar_entry(int(entry["entry_id"]), {"status": "approved"})
            released += 1
    db_commander_upsert_agent_state(agent_id, {"status": "LIVE", "held_count": 0})
    return {"agent_id": agent_id, "status": "LIVE", "released_count": released}
