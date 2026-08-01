#!/usr/bin/env python3
"""Append today's Demand OS ledger hygiene row if missing (no fake publish)."""
from __future__ import annotations

import csv
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs" / "ops" / "demand-os" / "set-now" / "LEDGER.csv"
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


def main() -> int:
    today = date.today().isoformat()
    if not LEDGER.is_file():
        print(f"FAIL: missing {LEDGER}")
        return 1

    with LEDGER.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
        fieldnames = list(rows[0].keys()) if rows else COLUMNS

    dates = {r.get("date") for r in rows}
    if today in dates:
        print(f"LEDGER_DAY: OK already has {today}")
        return 0

    utm = (
        "https://zzpackage.flexgrafik.nl/wizard/"
        "?utm_source=tiktok&utm_medium=organic"
        "&utm_campaign=icp_installateur&utm_content=tt_w31_install_01"
    )
    new = {
        "date": today,
        "channel": "tiktok",
        "icp_role": "installateur",
        "asset_id": "tt_w31_install_01",
        "utm_link": utm,
        "publish_Y/N": "N",
        "comments_sent": "0",
        "hot_leads": "0",
        "wizard_starts": "0",
        "paid": "0",
        "notes": f"hygiene auto-row · publish=N · fill after real activity · {today}",
    }
    with LEDGER.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames or COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow(r)
        w.writerow(new)
    print(f"LEDGER_DAY: APPENDED {today}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
