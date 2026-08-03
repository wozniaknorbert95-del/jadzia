"""Anti-spam — block identical copy across many FB groups (OS C.2)."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_REPO = Path(__file__).resolve().parents[3]
DEFAULT_SPAM_LOG = _REPO / "docs/ops/demand-os/set-now/ENGAGE-LOG.jsonl"


def default_engage_log_path() -> Path:
    """Writable engage log — prod set-now is read-only, fall back to data/."""
    from agent.demand_os.state_paths import resolve_writable_path

    return resolve_writable_path(DEFAULT_SPAM_LOG.name, env_var="DEMAND_OS_ENGAGE_LOG")

# Sniper: one fingerprint may hit at most ONE group per calendar day.
MAX_GROUP_TARGETS_PER_COPY_PER_DAY = 1


class AntiSpamError(PermissionError):
    """Duplicate engage copy blocked."""


def normalize_copy(text: str) -> str:
    t = (text or "").strip().lower()
    t = re.sub(r"\s+", " ", t)
    return t


def copy_fingerprint(text: str) -> str:
    return hashlib.sha256(normalize_copy(text).encode("utf-8")).hexdigest()[:24]


@dataclass
class EngageRecord:
    ts: str
    action: str
    target_id: str
    platform: str
    kind: str
    fingerprint: str
    dry_run: bool
    ok: bool
    notes: str = ""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def append_engage_log(record: Dict[str, Any], path: Optional[Path] = None) -> None:
    out = path or default_engage_log_path()
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def list_engage_log(path: Optional[Path] = None, *, limit: int = 200) -> List[Dict[str, Any]]:
    src = path or default_engage_log_path()
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
    return rows[-limit:] if limit > 0 else rows


def assert_comment_allowed(
    *,
    text: str,
    target_id: str,
    target_kind: str,
    path: Optional[Path] = None,
    as_of: Optional[date] = None,
) -> str:
    """
    Raise AntiSpamError if this copy already hit another group today.
    Own page / own account: always allowed (still logged).
    Returns fingerprint.
    """
    fp = copy_fingerprint(text)
    if target_kind not in ("group_nl", "group"):
        return fp

    day = (as_of or datetime.now(timezone.utc).date()).isoformat()
    hits = []
    for row in list_engage_log(path=path, limit=500):
        if row.get("action") != "comment":
            continue
        if not row.get("ok"):
            continue
        if row.get("fingerprint") != fp:
            continue
        if (row.get("ts") or "")[:10] != day:
            continue
        if row.get("kind") not in ("group_nl", "group"):
            continue
        tid = row.get("target_id")
        if tid and tid not in hits:
            hits.append(tid)

    other = [h for h in hits if h != target_id]
    if len(other) >= MAX_GROUP_TARGETS_PER_COPY_PER_DAY:
        raise AntiSpamError(
            f"spam_blocked: copy already used on group(s) {other} today "
            f"(max {MAX_GROUP_TARGETS_PER_COPY_PER_DAY} group/copy/day)"
        )
    if target_id in hits:
        # same group re-comment identical — still block mass replay
        raise AntiSpamError(
            f"spam_blocked: identical copy already sent to {target_id} today"
        )
    return fp


def make_log_record(
    *,
    action: str,
    target_id: str,
    platform: str,
    kind: str,
    text: str = "",
    dry_run: bool,
    ok: bool,
    notes: str = "",
) -> Dict[str, Any]:
    return {
        "ts": _utc_now(),
        "action": action,
        "target_id": target_id,
        "platform": platform,
        "kind": kind,
        "fingerprint": copy_fingerprint(text) if text else "",
        "dry_run": dry_run,
        "ok": ok,
        "notes": notes,
    }
