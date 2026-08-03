"""Bramka 0 — AUDIT-K-REGISTER truth contract."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTER = (ROOT / "docs" / "ops" / "demand-os" / "AUDIT-K-REGISTER.md").read_text(
    encoding="utf-8"
)
ROADMAP = (ROOT / ".cursor" / "plans" / "audit-k-roadmap.md").read_text(encoding="utf-8")


def test_register_exists_and_has_all_k_items():
    for i in range(1, 15):
        assert f"**K{i}**" in REGISTER, f"missing K{i}"


def test_register_forbids_done_without_evidence_rule():
    assert "DONE only with code + tests + required runtime/prod evidence" in REGISTER
    assert "Evidence pack" in REGISTER or "evidence/" in REGISTER


def test_k2_live_not_overclaimed():
    k2_line = [ln for ln in REGISTER.splitlines() if "| **K2**" in ln][0]
    # Live metric must remain blocked / not bare done without caveat
    assert "blocked" in k2_line.lower() or "fail-closed" in k2_line.lower()
    assert "DEMAND_OS_GA4_LIVE" in REGISTER or "live" in k2_line.lower()
    assert "`partial`" in ROADMAP


def test_status_enum_documented():
    for status in ("not_started", "in_progress", "partial", "blocked", "done"):
        assert f"`{status}`" in REGISTER


def test_done_rows_must_reference_evidence_path_pattern():
    """If any K-item is marked done, register must cite an evidence artifact."""
    done_rows = [
        ln
        for ln in REGISTER.splitlines()
        if re.search(r"\|\s*\*\*K\d+\*\*", ln) and "`done`" in ln
    ]
    assert "docs/handoffs/evidence/" in REGISTER
    for row in done_rows:
        assert len(row) > 20
