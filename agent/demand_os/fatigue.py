"""Creative fatigue check — OS B.4 (same asset > N days → warning)."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Optional

from agent.demand_os.ledger import read_ledger

FATIGUE_DAYS = 14


def fatigue_check(
    asset_id: str,
    *,
    as_of: Optional[date] = None,
    path: Optional[Path] = None,
    max_days: int = FATIGUE_DAYS,
) -> Dict[str, Any]:
    """Warn if asset_id published/used beyond creative fatigue window."""
    aid = (asset_id or "").strip()
    day = as_of or date.today()
    if not aid:
        return {"ok": False, "error": "asset_id required", "fatigue": False}
    first: Optional[date] = None
    hits = 0
    for row in read_ledger(path=path):
        if (row.get("asset_id") or "").strip() != aid:
            continue
        hits += 1
        raw = (row.get("date") or "").strip()
        try:
            d = date.fromisoformat(raw)
        except ValueError:
            continue
        if first is None or d < first:
            first = d
    if first is None:
        return {
            "ok": True,
            "fatigue": False,
            "asset_id": aid,
            "hits": 0,
            "note": "asset not in ledger",
        }
    age = (day - first).days
    tired = age >= max_days and hits >= 1
    return {
        "ok": True,
        "fatigue": tired,
        "asset_id": aid,
        "first_seen": first.isoformat(),
        "age_days": age,
        "max_days": max_days,
        "hits": hits,
        "warning": (
            f"B.4 creative fatigue: {aid} age={age}d ≥ {max_days} — new angle"
            if tired
            else ""
        ),
    }
