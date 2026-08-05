"""G5: canonical `python tools/demand_os_owner_verify.py` must import cleanly
without PYTHONPATH (script dir, not repo root, lands on sys.path). Regression
for the ModuleNotFoundError hit on prod 2026-08-05."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_owner_verify_importable_without_pythonpath():
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    env["JADZIA_TEST_NO_DOTENV"] = "1"
    proc = subprocess.run(
        [
            sys.executable,
            "-c",
            "import runpy; runpy.run_path("
            "'tools/demand_os_owner_verify.py', run_name='ov_bootstrap_test')",
        ],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, (proc.stderr or "")[-500:]


def test_hub_and_owner_verify_both_bootstrapped():
    src = (ROOT / "tools/demand_os_owner_verify.py").read_text(encoding="utf-8")
    bootstrap = "if str(ROOT) not in sys.path:"
    assert bootstrap in src
    assert src.index(bootstrap) < src.index("from agent.demand_os.doctor")
