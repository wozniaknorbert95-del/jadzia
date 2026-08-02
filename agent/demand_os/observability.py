"""Demand OS Observability — OS TARGET §M one screen (no vanity).

Reads ledger / validator log / engage log / calendar. No network.
"""

from __future__ import annotations

import csv
import json
import os
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _set_now() -> Path:
    env = os.environ.get("DEMAND_OS_SET_NOW")
    if env:
        return Path(env)
    return _repo_root() / "docs" / "ops" / "demand-os" / "set-now"


@dataclass
class ObservabilityScreen:
    """OS §M fields only — never views / VHQ / ops tickets."""

    publish_count: int = 0
    comments_sent: int = 0
    validator_fail: int = 0
    validator_pass: int = 0
    wizard_starts_by_utm: Dict[str, int] = field(default_factory=dict)
    paid_total: int = 0
    top_hook: str = ""
    hitl_queue: List[Dict[str, str]] = field(default_factory=list)
    ledger_rows: int = 0
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _read_ledger(path: Path) -> List[Dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _read_validator_log(path: Path) -> List[Dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _read_engage_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        return []
    out: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def _calendar_hitl(path: Path) -> List[Dict[str, str]]:
    """B1 — HITL queue with Desk vocab GOTOWY / BLOKADA / PREP (+ raw action)."""
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    slots = data.get("slots") or []
    queue: List[Dict[str, str]] = []
    for s in slots:
        status = (s.get("status") or "").lower()
        if status not in ("validated", "planned", "ready_for_human", "blocked"):
            continue
        if status == "validated":
            action, desk_action = "HITL_PUBLISH", "GOTOWY"
        elif status == "blocked":
            action, desk_action = "BLOCK", "BLOKADA"
        else:
            action, desk_action = "PREP", "PREP"
        queue.append(
            {
                "asset_id": s.get("asset_id") or "",
                "channel": s.get("channel") or "",
                "status": status,
                "action": action,
                "desk_action": desk_action,
            }
        )
    return queue


def build_screen(
    *,
    set_now: Optional[Path] = None,
    events_path: Optional[Path] = None,
) -> ObservabilityScreen:
    from agent.demand_os.starts_ingest import aggregate_starts_from_events

    root = set_now or _set_now()
    rows = _read_ledger(root / "LEDGER.csv")
    vrows = _read_validator_log(root / "VALIDATOR-LOG.csv")
    engage = _read_engage_jsonl(root / "ENGAGE-LOG.jsonl")
    hitl = _calendar_hitl(root / "CONTENT-CALENDAR.json")

    publish = 0
    comments = 0
    paid = 0
    starts_by: Dict[str, int] = defaultdict(int)
    hook_scores: Dict[str, int] = defaultdict(int)

    for r in rows:
        if (r.get("publish_Y/N") or "").strip().upper() == "Y":
            publish += 1
        try:
            comments += int(r.get("comments_sent") or 0)
        except ValueError:
            pass
        try:
            paid += int(r.get("paid") or 0)
        except ValueError:
            pass
        try:
            starts = int(r.get("wizard_starts") or 0)
        except ValueError:
            starts = 0
        utm = (r.get("utm_link") or "").strip()
        asset = (r.get("asset_id") or "").strip() or "unknown"
        if starts and utm:
            starts_by[utm] += starts
        if starts:
            hook_scores[asset] += starts
        if asset and asset not in hook_scores:
            hook_scores[asset] += 0

    # Prefer growth_events under set_now (no silent fall-back to repo default)
    ev_path = events_path if events_path is not None else (root / "GROWTH-EVENTS.jsonl")
    if ev_path.is_file():
        agg = aggregate_starts_from_events(events_path=ev_path)
        for utm, n in (agg.get("starts_by_utm") or {}).items():
            starts_by[utm] += int(n)
        paid += int(agg.get("paid") or 0)
        if agg.get("top_hook"):
            hook_scores[agg["top_hook"]] = hook_scores.get(agg["top_hook"], 0) + int(
                agg.get("starts_utm") or 0
            )
    else:
        agg = {"starts_by_utm": {}, "starts_utm": 0, "paid": 0, "top_hook": ""}

    for e in engage:
        if e.get("ok") is True and e.get("action") == "comment":
            comments += 1

    v_fail = 0
    v_pass = 0
    for v in vrows:
        dec = (v.get("decision") or v.get("result") or "").upper()
        if "FAIL" in dec:
            v_fail += 1
        elif "PASS" in dec:
            v_pass += 1

    top_hook = ""
    if any(hook_scores.values()):
        top_hook = max(hook_scores.items(), key=lambda kv: kv[1])[0]
    elif agg.get("top_hook"):
        top_hook = agg["top_hook"]
    elif rows:
        for r in reversed(rows):
            aid = (r.get("asset_id") or "").strip()
            if aid and (r.get("utm_link") or "").strip():
                top_hook = aid
                break

    return ObservabilityScreen(
        publish_count=publish,
        comments_sent=comments,
        validator_fail=v_fail,
        validator_pass=v_pass,
        wizard_starts_by_utm=dict(starts_by),
        paid_total=paid,
        top_hook=top_hook,
        hitl_queue=hitl,
        ledger_rows=len(rows),
        notes="OS §M — vanity metrics excluded; starts from growth_events+ledger",
    )


def money_check(
    *,
    set_now: Optional[Path] = None,
    events_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Poniedziałek Money Check slice (OS C.1 #8 / K)."""
    screen = build_screen(set_now=set_now, events_path=events_path)
    compliance = None
    total = screen.validator_pass + screen.validator_fail
    if total:
        compliance = round(screen.validator_pass / total, 4)
    from agent.demand_os.stl_monitor import stl_report

    stl = stl_report()
    return {
        "starts_utm": sum(screen.wizard_starts_by_utm.values()),
        "starts_by_utm": screen.wizard_starts_by_utm,
        "paid": screen.paid_total,
        "top_hook": screen.top_hook,
        "validator_fail": screen.validator_fail,
        "validator_pass": screen.validator_pass,
        "sniper_compliance": compliance,
        "publish_count": screen.publish_count,
        "comments_sent": screen.comments_sent,
        "stl_breaches": stl.get("breaches"),
        "stl_overnight": stl.get("overnight"),
        "stl_median_min": stl.get("median_min"),
        "kill_vanity": True,
    }
