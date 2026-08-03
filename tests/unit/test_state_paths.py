"""state_paths — writable runtime path contract (prod read-only set-now)."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent.demand_os.state_paths import resolve_writable_path


def test_env_override_wins(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    p = tmp_path / "custom.jsonl"
    monkeypatch.setenv("TEST_STATE_ENV", str(p))
    assert resolve_writable_path("X.jsonl", env_var="TEST_STATE_ENV") == p


def test_writable_set_now_default():
    # dev checkout is writable → set-now wins, no fallback
    out = resolve_writable_path("__probe_state__.jsonl")
    assert out.parent.name == "set-now"


def test_unwritable_set_now_falls_back(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    import agent.demand_os.state_paths as sp

    fake_set_now = tmp_path / "ro-set-now"
    fake_set_now.mkdir()
    monkeypatch.setattr(sp, "_SET_NOW_REL", fake_set_now.relative_to(tmp_path))
    monkeypatch.setattr(sp, "_REPO", tmp_path)
    monkeypatch.setattr(sp, "_FALLBACK_DIR", tmp_path / "data" / "demand-os")

    orig_write = Path.write_text

    def _ro_write(self: Path, *a, **k):
        if self.name == ".write_probe":
            raise OSError(13, "Permission denied")
        return orig_write(self, *a, **k)

    monkeypatch.setattr(Path, "write_text", _ro_write)
    out = resolve_writable_path("EVENTS.jsonl")
    assert out == tmp_path / "data" / "demand-os" / "EVENTS.jsonl"


def test_growth_events_append_uses_fallback(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    """Prod contract: validator emit must not crash on read-only set-now."""
    p = tmp_path / "events.jsonl"
    monkeypatch.setenv("DEMAND_OS_GROWTH_EVENTS", str(p))
    from agent.demand_os.growth_events import append_growth_event, list_growth_events

    rec = append_growth_event("cta_issued", asset_id="a1", channel="tiktok")
    assert rec["event_type"] == "cta_issued"
    assert list_growth_events(limit=1)[-1]["asset_id"] == "a1"


def test_calendar_save_uses_fallback(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    p = tmp_path / "cal.json"
    monkeypatch.setenv("DEMAND_OS_CONTENT_CALENDAR", str(p))
    from agent.demand_os.content_calendar import (
        ContentCalendar,
        default_calendar_path,
        save_calendar,
    )

    assert default_calendar_path() == p
    save_calendar(ContentCalendar(week="w31", slots=[], updated=""))
    assert p.is_file()
