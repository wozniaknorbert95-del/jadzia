"""8-09 — SoT tip pointer check: STATE.md prod_tip must match HEAD.

Runs green in two honest states:
- dirty working tree (dev mid-work) → skip: SoT is synced at ship time.
- clean tree (post-commit, VPS post-deploy) → prod_tip must equal `git HEAD`.

This catches "deployed c60ce52 but STATE.md still says 1981ad4" drift, which was
a real recurring defect class across sessions 6–8.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "docs" / "ops" / "demand-os" / "STATE.md"


def _git(*args: str) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=str(ROOT), capture_output=True, text=True, timeout=30
    )
    assert proc.returncode == 0, proc.stderr
    return proc.stdout.strip()


def _state_prod_tip() -> str:
    text = STATE.read_text(encoding="utf-8")
    m = re.search(r'prod_tip:\s*"([0-9a-f]{7,})', text)
    assert m, "STATE.md must carry `prod_tip: \"<sha> …\"` in the front matter"
    return m.group(1)


def test_state_md_prod_tip_matches_head_on_clean_tree():
    # Untracked files (runtime state, evidence, logs) do not block the check —
    # only tracked modifications mean "mid-work, SoT syncs later".
    if _git("status", "--porcelain", "--untracked-files=no"):
        pytest.skip("dirty tree — SoT tip syncs at ship time (8-10)")
    tip = _state_prod_tip()
    # SoT sync itself is a commit — accept tip at HEAD or HEAD~1 (tip-sync commit).
    heads = [
        _git("rev-parse", "--short", rev)
        for rev in ("HEAD", "HEAD~1")
        if subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", rev],
            cwd=str(ROOT),
            capture_output=True,
        ).returncode
        == 0
    ]
    assert any(h.startswith(tip) or tip.startswith(h) for h in heads), (
        f"STATE.md prod_tip={tip} not in {heads} — sync SoT before closing"
    )
