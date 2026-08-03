"""K14 GO-gated release helper."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_deploy_blocked_without_go():
    proc = subprocess.run(
        [sys.executable, "tools/commander_release.py", "deploy"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env={**dict(**__import__("os").environ), "COMMANDER_DEPLOY_GO": "secret-go"},
    )
    assert proc.returncode == 3
    data = json.loads(proc.stdout)
    assert data["blocked"] is True
    assert data["ok"] is False


def test_validate_runs():
    proc = subprocess.run(
        [sys.executable, "tools/commander_release.py", "validate"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    data = json.loads(proc.stdout)
    assert "cache" in data
    assert data["cache"].startswith("desk-dash")
    # ok depends on suite; structure must exist
    assert "errors" in data
    assert data["mode"] == "validate"


def test_rollback_hint_runs():
    proc = subprocess.run(
        [sys.executable, "tools/commander_release.py", "rollback-hint"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert data["mode"] == "rollback_hint"
    assert "commands" in data
