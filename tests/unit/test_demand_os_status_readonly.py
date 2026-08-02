"""Demand OS status GET must not mutate memory on read-only FS."""

from __future__ import annotations

import os
import stat
from pathlib import Path

from agent.demand_os.commander_status import build_demand_os_status


def test_build_demand_os_status_readonly_set_now(tmp_path: Path, monkeypatch):
    pack = tmp_path / "set-now"
    pack.mkdir()
    (pack / "LEDGER.csv").write_text(
        "date,channel,icp_role,asset_id,utm_link,publish_Y/N,comments_sent,hot_leads,wizard_starts,paid,notes\n"
        "2026-08-02,tiktok,installateur,tt_demo,https://zzpackage.flexgrafik.nl/wizard/?utm_source=tiktok&utm_medium=organic&utm_campaign=icp_installateur&utm_content=tt_demo,N,0,0,1,0,demo\n",
        encoding="utf-8",
    )
    (pack / "CONTENT-CALENDAR.json").write_text(
        '{"week":"2026-W32","updated":"2026-08-02","slots":[]}',
        encoding="utf-8",
    )
    (pack / "ALLOWLIST.json").write_text(
        '{"targets":[],"max_groups":1,"updated":"2026-08-02"}',
        encoding="utf-8",
    )
    (pack / "GROWTH-EVENTS.jsonl").write_text("", encoding="utf-8")
    mem = tmp_path / "MEMORY.json"
    mem.write_text('{"semantic":{"icp_role_week":"installateur"},"episodic":{},"procedural":{}}', encoding="utf-8")

    for p in (pack, mem):
        mode = p.stat().st_mode
        p.chmod(mode & ~stat.S_IWUSR)

    monkeypatch.setenv("DEMAND_OS_SET_NOW", str(pack))
    monkeypatch.setenv("DEMAND_OS_MEMORY", str(mem))

    out = build_demand_os_status(set_now=pack)
    assert out["ok"] is True
    assert "data_mode" in out
