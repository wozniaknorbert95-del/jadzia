"""Worker failure alerts — ALERTS.jsonl reader (MT-9/9-06 OPT-B).

The systemd alert unit (deployment/demand-os-agents-worker-alert.service) is
the only writer: it appends one json line per worker OnFailure event. This
module is the single read path, used by the doctor `worker_failures` check.

Semantics: an alert is ACTIVE while unresolved and younger than
ALERTS_MAX_AGE_H (auto-expire — no manual close workflow, no fake-green risk:
a still-failing worker appends a fresh line every tick, so RED persists
honestly). Tolerant by contract: missing file / bad lines / bad timestamps
mean "no alerts", never a crash — doctor must not die on observability.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

ALERTS_MAX_AGE_H = 24.0


def default_alerts_path() -> Path:
    """Resolve alerts path via the shared writable-path contract (like heartbeat)."""
    from agent.demand_os.state_paths import resolve_writable_path

    return resolve_writable_path("ALERTS.jsonl", env_var="DEMAND_OS_ALERTS_LOG")


def _parse_ts(value: Any) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def active_alerts(
    *,
    path: Optional[Path] = None,
    now: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    """Unresolved alerts younger than ALERTS_MAX_AGE_H, oldest first."""
    p = path or default_alerts_path()
    if not p.is_file():
        return []
    try:
        lines = p.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        logger.warning("alerts read failed %s: %s", p, exc)
        return []
    ref = now or datetime.now(timezone.utc)
    out: List[Dict[str, Any]] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue  # tolerant: a half-written line must not kill the check
        if not isinstance(rec, dict) or rec.get("resolved"):
            continue
        ts = _parse_ts(rec.get("ts"))
        if ts is None:
            continue
        age_h = (ref - ts).total_seconds() / 3600.0
        if age_h > ALERTS_MAX_AGE_H:
            continue  # auto-expire
        out.append(rec)
    return out
