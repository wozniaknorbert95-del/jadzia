"""HITL allowlist — max 5 FB groups + own surfaces (OS C.2)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

_REPO = Path(__file__).resolve().parents[3]
DEFAULT_ALLOWLIST_PATH = _REPO / "docs/ops/demand-os/set-now/ALLOWLIST.json"

ACTIVE = "active"
PENDING = "pending_fill"
PENDING_JOIN = "pending_join"
JOIN_REQUESTED = "join_requested"
RESEARCH = "research_selected"
GROUP_KINDS = frozenset({"group_nl", "group"})
OWN_KINDS = frozenset({"own_page", "own_account"})
# Engage only when active. Pipeline: research → pending_join → join_requested → active
JOIN_PIPELINE = frozenset({PENDING, PENDING_JOIN, JOIN_REQUESTED, RESEARCH})


class AllowlistError(PermissionError):
    """Target not allowed for engage."""


@dataclass(frozen=True)
class AllowlistTarget:
    id: str
    platform: str
    kind: str
    name: str
    external_id: str
    status: str
    notes: str = ""

    @property
    def is_group(self) -> bool:
        return self.kind in GROUP_KINDS

    @property
    def is_engageable(self) -> bool:
        return self.status == ACTIVE and bool(self.id)


def load_allowlist(path: Optional[Path] = None) -> Dict[str, Any]:
    src = path or DEFAULT_ALLOWLIST_PATH
    with src.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    max_groups = int(data.get("max_groups") or 10)
    if max_groups > 10:
        raise ValueError("max_groups hard cap is 10 (agency pack)")
    targets = [_parse_target(t) for t in (data.get("targets") or [])]
    groups = [t for t in targets if t.is_group]
    if len(groups) > max_groups:
        raise ValueError(f"allowlist has {len(groups)} groups > max_groups={max_groups}")
    return {
        "max_groups": max_groups,
        "updated": data.get("updated"),
        "research": data.get("research"),
        "targets": targets,
        "raw": data,
        "path": str(src),
    }


def _parse_target(raw: Dict[str, Any]) -> AllowlistTarget:
    return AllowlistTarget(
        id=str(raw.get("id") or "").strip(),
        platform=str(raw.get("platform") or "").strip().lower(),
        kind=str(raw.get("kind") or "").strip().lower(),
        name=str(raw.get("name") or "").strip(),
        external_id=str(raw.get("external_id") or "").strip(),
        status=str(raw.get("status") or PENDING).strip().lower(),
        notes=str(raw.get("notes") or "").strip(),
    )


def list_pending_join(path: Optional[Path] = None) -> List[AllowlistTarget]:
    return [
        t
        for t in load_allowlist(path)["targets"]
        if t.is_group and t.status in (PENDING_JOIN, JOIN_REQUESTED, RESEARCH, PENDING)
    ]


def set_target_status(
    target_id: str,
    status: str,
    *,
    path: Optional[Path] = None,
) -> AllowlistTarget:
    """Persist status change (e.g. pending_join → active after Join)."""
    status = (status or "").strip().lower()
    allowed = {ACTIVE, PENDING, PENDING_JOIN, JOIN_REQUESTED, RESEARCH}
    if status not in allowed:
        raise ValueError(f"status not allowed: {status}")
    src = path or DEFAULT_ALLOWLIST_PATH
    data = load_allowlist(path=src)
    raw = data["raw"]
    found = None
    for row in raw.get("targets") or []:
        if str(row.get("id") or "") == target_id:
            row["status"] = status
            found = _parse_target(row)
            break
    if found is None:
        raise AllowlistError(f"unknown target: {target_id}")
    raw["updated"] = __import__("datetime").datetime.now(
        __import__("datetime").timezone.utc
    ).date().isoformat()
    with src.open("w", encoding="utf-8") as fh:
        json.dump(raw, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return found


def list_active_targets(path: Optional[Path] = None) -> List[AllowlistTarget]:
    return [t for t in load_allowlist(path)["targets"] if t.is_engageable]


def get_target(target_id: str, path: Optional[Path] = None) -> Optional[AllowlistTarget]:
    tid = (target_id or "").strip()
    for t in load_allowlist(path)["targets"]:
        if t.id == tid:
            return t
    return None


def require_engage_target(target_id: str, path: Optional[Path] = None) -> AllowlistTarget:
    t = get_target(target_id, path=path)
    if t is None:
        raise AllowlistError(f"unknown target: {target_id}")
    if t.status != ACTIVE:
        raise AllowlistError(f"target not active: {target_id} status={t.status}")
    if t.platform not in ("facebook", "tiktok"):
        raise AllowlistError(f"platform not supported for F3: {t.platform}")
    return t
