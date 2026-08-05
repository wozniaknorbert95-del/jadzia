#!/usr/bin/env python3
"""Demand OS owner verify — one-shot pack (exit 0 = green).

Runs: doctor · pointer tests · pytest -k demand_os · footer full · go_day summary
· agents registry contract · agents wave-check (tool side).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(cmd: list[str], *, env: dict | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env=env,
        timeout=600,
    )


def main() -> int:
    env = {**os.environ, "PYTHONPATH": str(ROOT)}
    if not env.get("DEMAND_OS_SET_NOW"):
        env["DEMAND_OS_SET_NOW"] = "data/demand-os/set-now-sanitized"
    env.setdefault("PYTHONIOENCODING", "utf-8")

    errors: list[str] = []
    report: dict = {"ok": True, "steps": []}

    # 1) doctor
    from agent.demand_os.doctor import run_doctor

    doc = run_doctor()
    report["steps"].append(
        {"name": "doctor", "ok": doc.ok, "marketing": doc.marketing, "errors": doc.errors}
    )
    if not doc.ok:
        errors.append(f"doctor FAIL: {doc.errors}")

    # 2) pointer tests
    ptr = _run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_demand_os_tool_first_pointer.py",
            "-q",
            "--tb=line",
        ],
        env=env,
    )
    ptr_ok = ptr.returncode == 0
    report["steps"].append({"name": "pointer_tests", "ok": ptr_ok})
    if not ptr_ok:
        errors.append("pointer tests FAIL")
        errors.append((ptr.stdout or "")[-400:])

    # 3) demand_os suite
    suite = _run(
        [sys.executable, "-m", "pytest", "tests", "-k", "demand_os", "-q", "--tb=line"],
        env=env,
    )
    suite_ok = suite.returncode == 0
    report["steps"].append(
        {
            "name": "pytest_demand_os",
            "ok": suite_ok,
            "tail": (suite.stdout or "").strip().splitlines()[-3:],
        }
    )
    if not suite_ok:
        errors.append("pytest -k demand_os FAIL")

    # 4) footer full
    from agent.demand_os.commander_status import build_demand_os_status

    footer = build_demand_os_status(with_full_doctor=True).get("footer") or {}
    foot_ok = footer.get("doctor_scope") == "full" and isinstance(
        footer.get("doctor_ok"), bool
    )
    # doctor_ok should match full doctor when scope=full
    if foot_ok and footer.get("doctor_ok") is not True and doc.ok:
        foot_ok = False
        errors.append("footer.doctor_ok false while doctor ok")
    if foot_ok and not doc.ok and footer.get("doctor_ok") is True:
        foot_ok = False
        errors.append("footer false-green (doctor_ok true while doctor red)")
    report["steps"].append({"name": "footer_full", "ok": foot_ok, "footer": footer})
    if not foot_ok and "footer" not in " ".join(errors):
        errors.append("footer full check FAIL")

    # 5) go_day summary (artifact only)
    from agent.demand_os.week_ritual import go_day_ready

    go = go_day_ready()
    report["steps"].append(
        {
            "name": "go_day_ready",
            "ok": True,
            "score": go.get("score"),
            "marketing": go.get("marketing"),
            "marketing_hitl_gate": go.get("marketing_hitl_gate"),
            "note": "artifact score ≠ Tool/OPS SEAL",
        }
    )

    # 6) agents registry contract + wave readiness (TARGET v5 §J tool side)
    from agent.demand_os.agents.registry import all_roles, list_agents
    from agent.demand_os.agents.wave_check import wave_readiness

    roles = all_roles()
    listing = list_agents()
    # shell marker contract: cadence (worker-driven) roles flipped to False once
    # the worker timer proved itself on prod (2026-08-05); flow/HITL-only roles
    # stay shells. The contract checks consistency, not "all shells forever".
    from agent.demand_os.agents.registry import _WORKER_CADENCE_ROLES

    contract_ok = len(roles) == 9 and all(
        "live_allowed" in r
        and "heartbeat" in r
        and r.get("shell") is (r["role"] not in _WORKER_CADENCE_ROLES)
        for r in listing
    )
    report["steps"].append(
        {"name": "agents_registry_contract", "ok": contract_ok, "roles": len(roles)}
    )
    if not contract_ok:
        errors.append("agents registry contract FAIL")

    wr = wave_readiness()
    waves_ok = wr.get("ok") is True
    report["steps"].append(
        {
            "name": "agents_wave_check",
            "ok": waves_ok,
            "waves": [
                {"wave": w["wave"], "overall": w["overall"]} for w in wr.get("waves", [])
            ],
            "note": "tool_ready ≠ live PASS (human cadence after unlock)",
        }
    )
    if not waves_ok:
        errors.append("agents wave-check FAIL (tool side)")

    report["ok"] = not errors and all(s.get("ok") for s in report["steps"] if s["name"] != "go_day_ready")
    report["errors"] = errors
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
