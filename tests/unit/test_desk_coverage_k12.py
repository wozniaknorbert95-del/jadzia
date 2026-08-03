"""K12 — desk module coverage gate (≥80% line on core modules)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import agent.demand_os.attribution as attr
import agent.demand_os.commander_status as cs
import agent.demand_os.desk_contract as dc
import agent.demand_os.ga4_adapter as ga4
import agent.demand_os.ledger_export as lex
import agent.demand_os.sot_reconcile as sot

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs" / "handoffs" / "evidence" / "audit-k-2026-08-03" / "k12-coverage.txt"
MODULES = (
    "agent.demand_os.commander_status",
    "agent.demand_os.desk_contract",
    "agent.demand_os.ga4_adapter",
)
LINE_FLOOR = 80.0


def test_desk_modules_export_expected_surfaces():
    assert callable(cs.build_demand_os_status)
    assert callable(dc.resolve_robota_dnia)
    assert callable(dc.format_desk_pretty)
    assert callable(ga4.fetch_wizard_starts)
    assert callable(attr.ingest_wizard_start_event)
    assert callable(attr.sync_ops_bus_to_attribution)
    assert callable(sot.reconcile_dual_sot)
    assert callable(lex.export_ledger)


def test_desk_core_modules_line_coverage_gate():
    """Fail if core desk modules drop below 80% line coverage."""
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/unit/test_commander_status_ga4.py",
        "tests/unit/test_ga4_adapter.py",
        "tests/unit/test_attribution_k1.py",
        "tests/unit/test_sot_reconcile_k5.py",
        "tests/unit/test_ledger_export_k13.py",
        "tests/test_demand_os_desk_contract.py",
        "tests/unit/test_render_desk_golden.py",
        "tests/unit/test_demand_os_status_readonly.py",
        "--cov=agent.demand_os.commander_status",
        "--cov=agent.demand_os.desk_contract",
        "--cov=agent.demand_os.ga4_adapter",
        "--cov-report=term-missing",
        "--cov-report=json:docs/handoffs/evidence/audit-k-2026-08-03/k12-coverage.json",
        "-q",
    ]
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    cov_path = ROOT / "docs" / "handoffs" / "evidence" / "audit-k-2026-08-03" / "k12-coverage.json"
    assert cov_path.is_file(), "coverage json missing"
    data = json.loads(cov_path.read_text(encoding="utf-8"))
    files = data.get("files") or {}
    lines = []
    for mod in MODULES:
        # coverage.py keys are file paths
        match = next((v for k, v in files.items() if mod.replace(".", "/") in k.replace("\\", "/")), None)
        assert match is not None, f"missing coverage for {mod}"
        summary = match.get("summary") or {}
        pct = float(summary.get("percent_covered") or 0)
        lines.append(f"{mod}: {pct:.1f}% line")
        assert pct >= LINE_FLOOR, f"{mod} coverage {pct:.1f}% < {LINE_FLOOR}%"
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text("\n".join(lines) + f"\nfloor={LINE_FLOOR}\n", encoding="utf-8")
