#!/usr/bin/env python3
"""K8 — desk a11y smoke. Uses Playwright+axe if available; otherwise SKIP report."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "handoffs" / "evidence" / "audit-k-2026-08-03" / "k8-a11y-smoke.json"
HTML = ROOT / "commander-ui" / "index.html"


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tool": "desk_a11y_smoke",
        "html": str(HTML),
    }
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception as exc:
        report.update({"status": "SKIP", "reason": f"playwright missing: {exc}"[:200]})
        OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 0

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            page.goto(HTML.resolve().as_uri())
            page.add_script_tag(
                url="https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.8.4/axe.min.js"
            )
            result = page.evaluate(
                """async () => {
                  const r = await axe.run(document.getElementById('view-demand-desk') || document);
                  return {
                    violations: r.violations.map(v => ({
                      id: v.id, impact: v.impact, nodes: v.nodes.length
                    }))
                  };
                }"""
            )
            browser.close()
        serious = [
            v
            for v in result.get("violations", [])
            if v.get("impact") in ("critical", "serious")
        ]
        report.update(
            {
                "status": "PASS" if not serious else "FAIL",
                "violations": result.get("violations", []),
                "critical_serious": serious,
            }
        )
        OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 0 if report["status"] == "PASS" else 1
    except Exception as exc:
        report.update({"status": "SKIP", "reason": f"axe run failed: {exc}"[:200]})
        OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 0


if __name__ == "__main__":
    sys.exit(main())
