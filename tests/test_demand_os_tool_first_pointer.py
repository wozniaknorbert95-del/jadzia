"""Regression: Demand OS pointers stay tool/ops lane while live P0 is parked."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_todo_active_item_is_tool_or_ops_lane() -> None:
    todo = json.loads((ROOT / "todo.json").read_text(encoding="utf-8"))
    active = str(todo.get("active_item") or "")
    assert active.startswith("4-TOOL-") or active.startswith("4-OPS-"), (
        f"active_item={active!r} — expected 4-TOOL-* or 4-OPS-* while live P0 PARKED"
    )
    assert "2f68b64" not in str(todo.get("last_updated") or "")
    nh = str(todo.get("next_human") or "").lower()
    assert "publish" not in nh or "parked" in nh or "unlock" in nh or "optional" in nh


def test_master_todo_current_is_not_live_p0() -> None:
    text = (ROOT / "docs/ops/demand-os/MASTER-TODO-4.md").read_text(encoding="utf-8")
    block = re.search(r"```\nCURRENT:.*?\n```", text, flags=re.S)
    assert block, "MASTER-TODO-4 missing Aktywne zadanie fenced CURRENT block"
    current = block.group(0)
    assert "4-P0-01 ready_for_human" not in current
    assert "Dowódca publish tt_w32" not in current
    assert "4-TOOL-" in current or "4-OPS-" in current


def test_current_task_and_state_tool_first() -> None:
    current = (ROOT / ".cursor/current-task.md").read_text(encoding="utf-8")
    state = (ROOT / "docs/ops/demand-os/STATE.md").read_text(encoding="utf-8")
    session = (ROOT / ".cursor/session-state.md").read_text(encoding="utf-8")
    assert "TOOL" in current.upper() or "OPS" in current.upper()
    assert "PARKED" in current.upper()
    assert "4-P0-01 ready_for_human" not in current
    assert "2f68b64" not in current
    assert "2f68b64" not in session
    # Tip floor: TOOL-100 runtime 889258e or later OPS tip (a3deb59+)
    tip_ok = any(
        tip in current or tip in state for tip in ("a3deb59", "889258e")
    )
    assert tip_ok, "active pointers must cite prod tip a3deb59 (or seal floor 889258e)"
    assert "TOOL" in state.upper() and "PARKED" in state.upper()


def test_tool_first_rule_files_exist() -> None:
    assert (ROOT / ".cursor/rules/demand-os-tool-first.mdc").is_file()
    assert (ROOT / "docs/ops/demand-os/UNLOCK-LIVE-P0.md").is_file()
