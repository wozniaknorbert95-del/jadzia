"""Regression: Demand OS pointers must stay TOOL FIRST while live P0 is parked."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_todo_active_item_is_tool_lane() -> None:
    todo = json.loads((ROOT / "todo.json").read_text(encoding="utf-8"))
    active = str(todo.get("active_item") or "")
    assert active.startswith("4-TOOL-"), (
        f"active_item={active!r} — expected 4-TOOL-* while live P0 PARKED "
        "(see .cursor/rules/demand-os-tool-first.mdc)"
    )
    assert "publish" not in str(todo.get("next_human") or "").lower() or "parked" in str(
        todo.get("next_human") or ""
    ).lower()


def test_master_todo_current_is_tool_not_live_p0() -> None:
    text = (ROOT / "docs/ops/demand-os/MASTER-TODO-4.md").read_text(encoding="utf-8")
    block = re.search(r"```\nCURRENT:.*?\n```", text, flags=re.S)
    assert block, "MASTER-TODO-4 missing Aktywne zadanie fenced CURRENT block"
    current = block.group(0)
    assert "4-TOOL-" in current
    assert "4-P0-01 ready_for_human" not in current
    assert "Dowódca publish tt_w32" not in current


def test_current_task_and_state_tool_first() -> None:
    current = (ROOT / ".cursor/current-task.md").read_text(encoding="utf-8")
    state = (ROOT / "docs/ops/demand-os/STATE.md").read_text(encoding="utf-8")
    assert "TOOL" in current.upper()
    assert "PARKED" in current.upper()
    assert "4-P0-01 ready_for_human" not in current
    assert "TOOL" in state.upper() and "PARKED" in state.upper()


def test_tool_first_rule_files_exist() -> None:
    assert (ROOT / ".cursor/rules/demand-os-tool-first.mdc").is_file()
