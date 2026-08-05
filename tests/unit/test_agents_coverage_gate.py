"""8-07 — agents package coverage gate (≥80% line on agent/demand_os/agents/*).

Same pattern as K12 desk gate: run the agents test files under pytest-cov in a
subprocess, write evidence, fail under the floor.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import agent.demand_os.agents as agents_pkg
import agent.demand_os.agents.registry as reg

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "docs" / "handoffs" / "evidence" / "audit-k-2026-08-03"
MODULES = (
    "agent.demand_os.agents.registry",
    "agent.demand_os.agents.flow",
    "agent.demand_os.agents.wave_check",
    "agent.demand_os.agents.heartbeat",
    "agent.demand_os.agents.worker",
    "agent.demand_os.agents.wave1",
)
LINE_FLOOR = 80.0


def test_agents_package_exports_worker_surface():
    assert callable(agents_pkg.dispatch)
    assert callable(agents_pkg.run_due)
    assert callable(agents_pkg.due_actions)
    assert callable(reg.list_agents)


def test_agents_modules_line_coverage_gate(tmp_path: Path):
    """Fail if agents modules drop below 80% line coverage.

    S7: evidence writes to docs/handoffs/evidence only when
    JADZIA_EVIDENCE_WRITE=1 (local/CI refresh). Default run writes to tmp —
    a test suite must leave a clean git tree.
    """
    write_evidence = os.environ.get("JADZIA_EVIDENCE_WRITE") == "1"
    cov_json = (EVIDENCE_DIR if write_evidence else tmp_path) / "k12-coverage-agents.json"
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/unit/test_agents_registry.py",
        "tests/unit/test_agents_flow_wave.py",
        "tests/unit/test_agents_heartbeat.py",
        "tests/unit/test_agents_worker.py",
        "--cov=agent.demand_os.agents",
        "--cov-report=term-missing",
        f"--cov-report=json:{cov_json}",
        "-q",
    ]
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert cov_json.is_file(), "coverage json missing"
    data = json.loads(cov_json.read_text(encoding="utf-8"))
    files = data.get("files") or {}
    lines = []
    for mod in MODULES:
        match = next(
            (v for k, v in files.items() if mod.replace(".", "/") in k.replace("\\", "/")),
            None,
        )
        assert match is not None, f"missing coverage for {mod}"
        summary = match.get("summary") or {}
        pct = float(summary.get("percent_covered") or 0)
        lines.append(f"{mod}: {pct:.1f}% line")
        assert pct >= LINE_FLOOR, f"{mod} coverage {pct:.1f}% < {LINE_FLOOR}%"
    if write_evidence:
        (EVIDENCE_DIR / "k12-coverage-agents.txt").write_text(
            "\n".join(lines) + f"\nfloor={LINE_FLOOR}\n", encoding="utf-8"
        )
