"""Demand OS F3 — allowlist, anti-spam, engage smoke."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent.demand_os.connectors.allowlist import (
    AllowlistError,
    list_active_targets,
    load_allowlist,
    require_engage_target,
)
from agent.demand_os.connectors.anti_spam import AntiSpamError, assert_comment_allowed
from agent.demand_os.connectors.engage import comment_on_target, read_target
from agent.demand_os.utm_lock import build_wizard_utm


@pytest.fixture
def allowlist_file(tmp_path: Path) -> Path:
    data = {
        "max_groups": 5,
        "targets": [
            {
                "id": "fb_own_page",
                "platform": "facebook",
                "kind": "own_page",
                "name": "Own",
                "external_id": "page1",
                "status": "active",
            },
            {
                "id": "tt_own",
                "platform": "tiktok",
                "kind": "own_account",
                "name": "@x",
                "external_id": "x",
                "status": "active",
            },
            {
                "id": "fb_g1",
                "platform": "facebook",
                "kind": "group_nl",
                "name": "Bouw 1",
                "external_id": "g1",
                "status": "active",
            },
            {
                "id": "fb_g2",
                "platform": "facebook",
                "kind": "group_nl",
                "name": "Bouw 2",
                "external_id": "g2",
                "status": "active",
            },
            {
                "id": "fb_g3",
                "platform": "facebook",
                "kind": "group_nl",
                "name": "",
                "external_id": "",
                "status": "pending_fill",
            },
        ],
    }
    path = tmp_path / "ALLOWLIST.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_repo_allowlist_max_groups():
    data = load_allowlist()
    groups = [t for t in data["targets"] if t.is_group]
    assert data["max_groups"] == 10
    assert len(groups) == 10
    assert len(groups) <= data["max_groups"]
    active = list_active_targets()
    assert any(t.id == "fb_own_page" for t in active)
    assert any(t.id == "tt_own" for t in active)
    # After personal join wave: mix of active + join_requested (no empty pending_join slots)
    assert all(t.external_id for t in groups)
    statuses = {t.status for t in groups}
    assert statuses <= {"active", "join_requested", "pending_join"}
    assert any(t.status == "active" for t in groups)
    assert any(t.status == "join_requested" for t in groups)


def test_pending_fill_denied(allowlist_file: Path):
    with pytest.raises(AllowlistError):
        require_engage_target("fb_g3", path=allowlist_file)


def test_unknown_denied(allowlist_file: Path):
    with pytest.raises(AllowlistError):
        require_engage_target("nope", path=allowlist_file)


def test_read_smoke(allowlist_file: Path, tmp_path: Path):
    log = tmp_path / "engage.jsonl"
    res = read_target(
        "fb_own_page",
        mode="mock",
        allowlist_path=allowlist_file,
        log_path=log,
    )
    assert res.ok
    assert res.items


def test_comment_smoke_with_utm(allowlist_file: Path, tmp_path: Path):
    log = tmp_path / "engage.jsonl"
    url = build_wizard_utm("tiktok", "installateur", "tt_engage_01")
    body = f"Herkenbare bus helpt. Start Wizard:\n{url}"
    out = comment_on_target(
        "tt_own",
        body,
        mode="mock",
        dry_run=True,
        asset_id="tt_engage_01",
        allowlist_path=allowlist_file,
        log_path=log,
    )
    assert out["ok"]
    assert out["validator"]["decision"] == "PASS"


def test_anti_spam_blocks_second_group(allowlist_file: Path, tmp_path: Path):
    log = tmp_path / "engage.jsonl"
    url = build_wizard_utm("facebook", "installateur", "fb_engage_01")
    body = f"Zelfde copy spam test.\n{url}"
    out1 = comment_on_target(
        "fb_g1",
        body,
        mode="mock",
        dry_run=True,
        asset_id="fb_engage_01",
        allowlist_path=allowlist_file,
        log_path=log,
    )
    assert out1["ok"]
    with pytest.raises(AntiSpamError):
        comment_on_target(
            "fb_g2",
            body,
            mode="mock",
            dry_run=True,
            asset_id="fb_engage_01",
            allowlist_path=allowlist_file,
            log_path=log,
        )


def test_assert_comment_allowed_own_exempt(tmp_path: Path):
    log = tmp_path / "e.jsonl"
    fp = assert_comment_allowed(
        text="hello",
        target_id="fb_own_page",
        target_kind="own_page",
        path=log,
    )
    assert fp
