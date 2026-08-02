#!/usr/bin/env python3
"""Demand OS Phase 0 (SET NOW) verifier — no network, docs-only.

Exit 0 = Phase 0 PASS (agent-side artifacts present).
Exit 1 = FAIL (missing files / ledger columns / empty test row).
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SET_NOW = ROOT / "docs" / "ops" / "demand-os" / "set-now"

REQUIRED_FILES = [
    "README.md",
    "ICP-WEEK.md",
    "PRIMARY-CHANNEL.md",
    "UTM-TEMPLATE.md",
    "ADS-FREEZE.md",
    "STL-CHECKLIST.md",
    "DA-WIZARD-NL.md",
    "MONEY-CHECK.md",
    "FB-ALLOWLIST.md",
    "TT-ENGAGE.md",
    "BLOG-ICP-W1.md",
    "VALIDATOR-CHECKLIST.md",
    "WAVE1-ROSTER.md",
    "ICP-BRIEF-W1.md",
    "LEDGER.csv",
]

LEDGER_COLUMNS = [
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

MUST_CONTAIN = {
    "ICP-WEEK.md": "installateur",
    "PRIMARY-CHANNEL.md": "2026-08-02",
    "UTM-TEMPLATE.md": "utm_source={channel}",
    "WAVE1-ROSTER.md": "Sniper_Validator",
    "VALIDATOR-CHECKLIST.md": "Brak UTM",
}

# Ads SoT: calendar freeze (legacy) OR cash park (Organic Sprint)
ADS_FREEZE_OK = ("parked_cash", "2026-08-06")


def main() -> int:
    errors: list[str] = []

    if not SET_NOW.is_dir():
        print(f"FAIL: missing dir {SET_NOW}")
        return 1

    for name in REQUIRED_FILES:
        path = SET_NOW / name
        if not path.is_file():
            errors.append(f"missing file: {name}")
            continue
        text = path.read_text(encoding="utf-8")
        needle = MUST_CONTAIN.get(name)
        if needle and needle not in text:
            errors.append(f"{name}: expected substring {needle!r}")
        if name == "ADS-FREEZE.md" and not any(s in text for s in ADS_FREEZE_OK):
            errors.append(
                f"ADS-FREEZE.md: expected one of {ADS_FREEZE_OK!r}"
            )

    ledger_path = SET_NOW / "LEDGER.csv"
    if ledger_path.is_file():
        with ledger_path.open(encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames != LEDGER_COLUMNS:
                errors.append(
                    f"LEDGER.csv columns mismatch.\n"
                    f"  got:  {reader.fieldnames}\n"
                    f"  want: {LEDGER_COLUMNS}"
                )
            rows = list(reader)
            if len(rows) < 1:
                errors.append("LEDGER.csv needs ≥1 data row (test row)")
            else:
                row = rows[0]
                if row.get("icp_role") != "installateur":
                    errors.append("LEDGER test row icp_role must be installateur")
                if "utm_source=" not in (row.get("utm_link") or ""):
                    errors.append("LEDGER test row utm_link must include utm_source=")

    if errors:
        print("Phase 0 CHECK: FAIL")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("Phase 0 CHECK: PASS")
    print(f"  artifacts: {len(REQUIRED_FILES)} files under {SET_NOW.relative_to(ROOT)}")
    print("  ads: parked_cash OR calendar freeze marker present")
    print("  next: TOOL/PROGRAM SEAL maintain — marketing PARKED_LAST until GO MARKETING HITL")
    print("  stop: live publish/hunt · Ads F5 · VPS without GO")
    return 0


if __name__ == "__main__":
    sys.exit(main())
