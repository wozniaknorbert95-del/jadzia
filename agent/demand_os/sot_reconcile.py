"""K5 — Dual SoT reconcile (SQLite authority vs file projection). Dry-run default."""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent.demand_os.desk_contract import set_now_path


@dataclass
class DriftItem:
    kind: str
    key: str
    detail: str

    def to_dict(self) -> Dict[str, str]:
        return {"kind": self.kind, "key": self.key, "detail": self.detail}


def _file_checksum(path: Path) -> str:
    if not path.is_file():
        return ""
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()[:16]


def _count_growth_starts(events_path: Path) -> int:
    if not events_path.is_file():
        return 0
    n = 0
    for line in events_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (rec.get("event_type") or "") == "wizard_start":
            n += 1
    return n


def _sqlite_attributed_total(db_path: Optional[Path] = None) -> int:
    from agent.demand_os.attribution import attribution_summary

    return int(attribution_summary(db_path=db_path).get("total") or 0)


def reconcile_dual_sot(
    *,
    set_now: Optional[Path] = None,
    db_path: Optional[Path] = None,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """
    Compare SQLite attribution authority vs GROWTH-EVENTS / LEDGER projection.
    dry_run=True never writes. Returns drift list + checksums.
    """
    root = set_now or set_now_path()
    events = root / "GROWTH-EVENTS.jsonl"
    ledger = root / "LEDGER.csv"
    drift: List[DriftItem] = []

    sqlite_total = _sqlite_attributed_total(db_path=db_path)
    file_starts = _count_growth_starts(events)

    if sqlite_total and not events.is_file():
        drift.append(
            DriftItem(
                "missing_projection",
                "GROWTH-EVENTS.jsonl",
                f"sqlite has {sqlite_total} starts; file missing",
            )
        )
    elif abs(sqlite_total - file_starts) > 0 and (sqlite_total or file_starts):
        drift.append(
            DriftItem(
                "count_mismatch",
                "wizard_start",
                f"sqlite={sqlite_total} file={file_starts}",
            )
        )

    ledger_starts = 0
    if ledger.is_file():
        with ledger.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                try:
                    ledger_starts += int(row.get("wizard_starts") or 0)
                except ValueError:
                    pass
    # Ledger is cumulative operational; warn only when file events >> ledger with no notes.
    if file_starts > 0 and ledger_starts == 0 and events.is_file():
        drift.append(
            DriftItem(
                "ledger_lag",
                "LEDGER.csv",
                f"growth_events starts={file_starts} but ledger wizard_starts sum=0",
            )
        )

    report = {
        "ok": len(drift) == 0,
        "dry_run": dry_run,
        "authority": "sqlite:demand_wizard_starts",
        "projection": str(root),
        "sqlite_total": sqlite_total,
        "growth_events_starts": file_starts,
        "ledger_starts_sum": ledger_starts,
        "checksums": {
            "GROWTH-EVENTS.jsonl": _file_checksum(events),
            "LEDGER.csv": _file_checksum(ledger),
        },
        "drift": [d.to_dict() for d in drift],
        "repair": "use tools/demand_os_ledger_export.py --apply after review (never invent)",
    }
    return report
