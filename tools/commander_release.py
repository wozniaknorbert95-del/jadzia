#!/usr/bin/env python3
"""K14 — GO-gated Commander UI release helper.

validate: local checks only (no SSH)
deploy: requires --go TOKEN matching COMMANDER_DEPLOY_GO env (fresh GO)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "commander-ui" / "index.html"
SW = ROOT / "commander-ui" / "sw.js"
MANIFEST_DIR = ROOT / "docs" / "handoffs" / "evidence" / "releases"


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _cache_version() -> str:
    text = HTML.read_text(encoding="utf-8")
    m = re.search(r"[?&]v=(desk-dash\d+)", text)
    return m.group(1) if m else ""


def _git_sha() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(ROOT),
            text=True,
        ).strip()
        return out
    except Exception:
        return "unknown"


def validate() -> dict:
    cache = _cache_version()
    sw = SW.read_text(encoding="utf-8")
    errors = []
    if not cache:
        errors.append("missing desk-dash cache bust in index.html")
    if cache and f"coi-commander-{cache}" not in sw:
        errors.append(f"sw.js CACHE mismatch vs {cache}")
    # targeted tests
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/unit/test_demand_desk_ui_contracts.py",
        "tests/unit/test_ga4_adapter.py",
        "tests/unit/test_audit_k_register.py",
        "-q",
    ]
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    if proc.returncode != 0:
        errors.append("pytest failed:\n" + (proc.stdout or "")[-500:])
    report = {
        "ok": not errors,
        "mode": "validate",
        "sha": _git_sha(),
        "cache": cache,
        "generated_at": _utc(),
        "errors": errors,
        "pytest_tail": (proc.stdout or "").strip().splitlines()[-5:],
    }
    return report


def deploy(*, go_token: str) -> dict:
    expected = (os.getenv("COMMANDER_DEPLOY_GO") or "").strip()
    if not go_token or not expected or go_token != expected:
        return {
            "ok": False,
            "mode": "deploy",
            "blocked": True,
            "error": "Deploy blocked — missing/invalid --go (fresh GO required; Zasada 11)",
            "sha": _git_sha(),
            "cache": _cache_version(),
            "generated_at": _utc(),
        }
    # Never SSH autonomously here — emit manifest for human/ops playbook.
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "ok": True,
        "mode": "deploy_manifest",
        "sha": _git_sha(),
        "cache": _cache_version(),
        "generated_at": _utc(),
        "go_present": True,
        "next": "Run .agents/workflows/jadzia-deploy.md manually with this manifest",
    }
    path = MANIFEST_DIR / f"commander-{manifest['sha']}-{manifest['cache']}.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    manifest["manifest_path"] = str(path)
    return manifest


def main() -> int:
    p = argparse.ArgumentParser(description="Commander UI release (GO-gated)")
    p.add_argument("command", choices=["validate", "deploy"])
    p.add_argument("--go", default="", help="Fresh GO token matching COMMANDER_DEPLOY_GO")
    args = p.parse_args()
    if args.command == "validate":
        report = validate()
    else:
        report = deploy(go_token=args.go)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if report.get("blocked"):
        return 3
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
