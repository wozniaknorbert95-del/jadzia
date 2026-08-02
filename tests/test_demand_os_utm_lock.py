"""Demand OS F1 — UTM Lock + growth_events."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent.demand_os.growth_events import append_growth_event, list_growth_events
from agent.demand_os.utm_lock import (
    UtmLockError,
    build_wizard_utm,
    canonical_form,
    validate_utm_url,
)


def test_build_wizard_utm_template():
    url = build_wizard_utm("tiktok", "installateur", "tt_w31_install_01")
    assert url.startswith("https://zzpackage.flexgrafik.nl/wizard/?")
    assert "utm_source=tiktok" in url
    assert "utm_medium=organic" in url
    assert "utm_campaign=icp_installateur" in url
    assert "utm_content=tt_w31_install_01" in url


def test_build_rejects_bad_channel():
    with pytest.raises(UtmLockError):
        build_wizard_utm("myspace", "installateur", "x")


def test_validate_pass():
    url = build_wizard_utm("whatsapp", "installateur", "wa_w31_install_01")
    result = validate_utm_url(url)
    assert result["ok"] is True
    assert result["parts"]["channel"] == "whatsapp"


def test_validate_bare_wizard_fails():
    result = validate_utm_url("https://zzpackage.flexgrafik.nl/wizard/")
    assert result["ok"] is False
    assert any("utm_source" in e for e in result["errors"])


def test_validate_multi_cta_fails():
    a = build_wizard_utm("tiktok", "installateur", "a")
    b = build_wizard_utm("tiktok", "installateur", "b")
    result = validate_utm_url(f"{a} also {b}")
    assert result["ok"] is False
    assert any("multi_cta" in e for e in result["errors"])


def test_validate_hq_vanity_fails():
    result = validate_utm_url(
        "https://flexgrafik.nl/?utm_source=tiktok&utm_medium=organic"
        "&utm_campaign=icp_installateur&utm_content=x"
    )
    assert result["ok"] is False


def test_canonical_form():
    url = build_wizard_utm("blog", "installateur", "blog_w31_install_01")
    assert canonical_form(url) == url


def test_growth_events_append(tmp_path: Path):
    path = tmp_path / "events.jsonl"
    url = build_wizard_utm("tiktok", "installateur", "tt_test")
    rec = append_growth_event(
        "cta_issued",
        asset_id="tt_test",
        channel="tiktok",
        utm_link=url,
        ok=True,
        path=path,
    )
    assert rec["event_type"] == "cta_issued"
    rows = list_growth_events(path=path)
    assert len(rows) == 1
    assert rows[0]["asset_id"] == "tt_test"
