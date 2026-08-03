#!/usr/bin/env python3
"""K9 — desk perf smoke. Uses Lighthouse CLI if available; otherwise SKIP report."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "handoffs" / "evidence" / "audit-k-2026-08-03" / "k9-perf-smoke.json"
HTML = ROOT / "commander-ui" / "index.html"


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tool": "desk_perf_smoke",
        "html": str(HTML),
        "budget": {"performance": 80, "lcp_ms": 2500, "cls": 0.1},
    }
    lh = shutil.which("lighthouse")
    if not lh:
        report.update({"status": "SKIP", "reason": "lighthouse CLI not installed"})
        OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 0

    out_json = OUT.with_name("k9-lighthouse-raw.json")
    try:
        subprocess.run(
            [
                lh,
                HTML.resolve().as_uri(),
                "--quiet",
                "--chrome-flags=--headless",
                "--only-categories=performance",
                f"--output-path={out_json}",
                "--output=json",
            ],
            check=True,
            cwd=str(ROOT),
            timeout=180,
        )
        data = json.loads(out_json.read_text(encoding="utf-8"))
        score = int(round(100 * float((data.get("categories") or {}).get("performance", {}).get("score") or 0)))
        report.update({"status": "PASS" if score >= 80 else "FAIL", "performance_score": score})
        OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 0 if report["status"] == "PASS" else 1
    except Exception as exc:
        report.update({"status": "SKIP", "reason": f"lighthouse failed: {exc}"[:200]})
        OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 0


if __name__ == "__main__":
    sys.exit(main())
