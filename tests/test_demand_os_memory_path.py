"""MEMORY path honesty — writable path + fail-closed logging."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent.demand_os.memory import default_memory_path, load_memory, save_memory, set_semantic_icp


def test_demand_os_memory_env_wins(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    target = tmp_path / "MEMORY.json"
    monkeypatch.setenv("DEMAND_OS_MEMORY", str(target))
    assert default_memory_path() == target
    store = load_memory()
    store["semantic"]["icp_role_week"] = "installateur"
    save_memory(store)
    assert target.is_file()
    data = json.loads(target.read_text(encoding="utf-8"))
    assert data["semantic"]["icp_role_week"] == "installateur"


def test_set_semantic_icp_roundtrip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DEMAND_OS_MEMORY", str(tmp_path / "MEMORY.json"))
    out = set_semantic_icp("installateur", "witte bus")
    assert out["semantic"]["icp_role_week"] == "installateur"
    reloaded = load_memory()
    assert reloaded["semantic"]["hook_nl"] == "witte bus"
