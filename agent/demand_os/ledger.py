"""OS C.7 ledger — CSV SoT helpers (no fake publish/starts)."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

_REPO = Path(__file__).resolve().parents[2]
DEFAULT_LEDGER = _REPO / "docs/ops/demand-os/set-now/LEDGER.csv"

COLUMNS = [
    "date",
    "channel",
    "icp_role",
    "asset_id",
    "utm_link",
    "publish_Y/N",
    "comments_sent",
    "hot_leads",
    "wizard_starts",
    "paid",
    "notes",
]


def ledger_path(path: Optional[Path] = None) -> Path:
    return path or DEFAULT_LEDGER


def read_ledger(*, path: Optional[Path] = None) -> List[Dict[str, str]]:
    src = ledger_path(path)
    if not src.is_file():
        return []
    with src.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def ledger_summary(*, path: Optional[Path] = None, days: int = 14) -> Dict[str, Any]:
    rows = read_ledger(path=path)
    published = sum(1 for r in rows if (r.get("publish_Y/N") or "").upper() == "Y")
    comments = sum(int(r.get("comments_sent") or 0) for r in rows)
    starts = sum(int(r.get("wizard_starts") or 0) for r in rows)
    paid = sum(int(r.get("paid") or 0) for r in rows)
    today = date.today().isoformat()
    has_today = any(r.get("date") == today for r in rows)
    return {
        "ok": True,
        "rows": len(rows),
        "published_y": published,
        "comments_sent": comments,
        "wizard_starts": starts,
        "paid": paid,
        "has_today_row": has_today,
        "today": today,
        "days_window_note": days,
        "path": str(ledger_path(path)),
        "w1_pass_signal": published >= 3 and len(rows) >= 7,
        "marketing": "PARKED_LAST",
    }


def ensure_today_row(
    *,
    path: Optional[Path] = None,
    channel: str = "tiktok",
    icp_role: str = "installateur",
    asset_id: str = "tt_hygiene",
    dry_run: bool = False,
) -> Dict[str, Any]:
    from agent.demand_os.utm_lock import build_wizard_utm

    src = ledger_path(path)
    rows = read_ledger(path=src)
    today = date.today().isoformat()
    if any(r.get("date") == today for r in rows):
        return {"ok": True, "action": "exists", "date": today, "dry_run": dry_run}
    utm = build_wizard_utm(channel, icp_role, asset_id)
    new = {
        "date": today,
        "channel": channel,
        "icp_role": icp_role,
        "asset_id": asset_id,
        "utm_link": utm,
        "publish_Y/N": "N",
        "comments_sent": "0",
        "hot_leads": "0",
        "wizard_starts": "0",
        "paid": "0",
        "notes": f"hygiene auto-row · publish=N · {today}",
    }
    if dry_run:
        return {"ok": True, "action": "would_append", "row": new, "dry_run": True}
    fieldnames = list(rows[0].keys()) if rows else COLUMNS
    with src.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
        w.writerow(new)
    return {"ok": True, "action": "appended", "date": today, "dry_run": False}
