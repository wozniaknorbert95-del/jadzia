"""Demand OS F2 — Sniper Validator + content_calendar."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from agent.demand_os.content_calendar import (
    CalendarSlot,
    ContentCalendar,
    add_slot,
    assert_publish_allowed,
    save_calendar,
    set_slot_status,
)
from agent.demand_os.publish_request import PublishRequest
from agent.demand_os.utm_lock import build_wizard_utm
from agent.demand_os.validator import (
    RULE_R1_MULTI_CTA_URL,
    RULE_R2_UTM_MISSING,
    RULE_R3_ICP_ROLE,
    RULE_R4_MULTI_CTA_WORDS,
    RULE_R5_ADS_FREEZE,
    RULE_R6_HQ_HERO,
    RULE_R7_OFFERTE_ONLY,
    RULE_R8_GAME_DUAL_CTA,
    evaluate_publish_request,
)


def _req(**kwargs) -> PublishRequest:
    base = dict(
        asset_id="tt_w31_install_01",
        channel="tiktok",
        icp_role="installateur",
        caption=(
            "Witte bus = anoniem. Branding = herkenbaar.\n"
            "#installateur #zzp\n"
        ),
        utm_link=build_wizard_utm("tiktok", "installateur", "tt_w31_install_01"),
        content_type="organic_post",
    )
    base.update(kwargs)
    return PublishRequest(**base)


def _eval(req: PublishRequest, tmp_path: Path, **kwargs):
    return evaluate_publish_request(
        req,
        log=True,
        log_path=tmp_path / "VALIDATOR-LOG.csv",
        emit_events=False,
        **kwargs,
    )


def test_pass_clean_organic(tmp_path: Path):
    d = _eval(_req(), tmp_path)
    assert d.ok
    assert d.pass_token and d.pass_token.startswith("val_")
    assert d.decision_ms >= 0


def test_r1_multi_url(tmp_path: Path):
    u1 = build_wizard_utm("tiktok", "installateur", "a")
    u2 = build_wizard_utm("tiktok", "installateur", "b")
    d = _eval(_req(caption=f"Go {u1} and also {u2} #installateur", utm_link=u1), tmp_path)
    assert not d.ok
    assert RULE_R1_MULTI_CTA_URL in d.fail_rules


def test_r2_bare_wizard(tmp_path: Path):
    d = _eval(
        _req(utm_link="https://zzpackage.flexgrafik.nl/wizard/", caption="#installateur x"),
        tmp_path,
    )
    assert not d.ok
    assert RULE_R2_UTM_MISSING in d.fail_rules


def test_r3_role_mismatch(tmp_path: Path):
    d = _eval(
        _req(
            icp_role="loodgieter",
            caption="Bus branding #loodgieter",
            utm_link=build_wizard_utm("tiktok", "installateur", "tt_w31_install_01"),
        ),
        tmp_path,
    )
    assert not d.ok
    assert RULE_R3_ICP_ROLE in d.fail_rules


def test_r4_multi_cta_words(tmp_path: Path):
    d = _eval(_req(caption="Like and comment for Wizard #installateur"), tmp_path)
    assert not d.ok
    assert RULE_R4_MULTI_CTA_WORDS in d.fail_rules


def test_r5_ads_freeze(tmp_path: Path):
    d = _eval(_req(ads_boost=True), tmp_path, as_of=date(2026, 8, 1))
    assert not d.ok
    assert RULE_R5_ADS_FREEZE in d.fail_rules


def test_r5_paid_utm_after_thaw_ok(tmp_path: Path):
    utm = build_wizard_utm("meta", "installateur", "meta_boost_w31_01", medium="paid")
    d = _eval(
        _req(
            channel="meta",
            asset_id="meta_boost_w31_01",
            utm_link=utm,
            caption="Paid test #installateur",
            ads_boost=True,
        ),
        tmp_path,
        as_of=date(2026, 8, 6),
    )
    assert d.ok


def test_r6_hq_hero(tmp_path: Path):
    d = _eval(_req(hero_is_hq=True), tmp_path)
    assert RULE_R6_HQ_HERO in d.fail_rules


def test_r7_offerte_only(tmp_path: Path):
    d = _eval(_req(caption="Vraag offerte via mail #installateur", utm_link=_req().utm_link), tmp_path)
    assert RULE_R7_OFFERTE_ONLY in d.fail_rules


def test_r8_game_dual(tmp_path: Path):
    d = _eval(
        PublishRequest(
            asset_id="game_01",
            channel="tiktok",
            icp_role="installateur",
            content_type="game_post",
            caption="Play https://app.flexgrafik.nl and Wizard too",
            utm_link=build_wizard_utm("tiktok", "installateur", "game_01"),
        ),
        tmp_path,
    )
    assert RULE_R8_GAME_DUAL_CTA in d.fail_rules


def test_calendar_gate(tmp_path: Path):
    path = tmp_path / "cal.json"
    cal = ContentCalendar(week="2026-W32", slots=[])
    cal = add_slot(
        cal,
        CalendarSlot(
            date="2026-08-03",
            channel="tiktok",
            asset_id="tt_w31_install_02",
            status="planned",
        ),
    )
    save_calendar(cal, path)
    with pytest.raises(PermissionError):
        assert_publish_allowed(cal, "tt_w31_install_02")

    d = _eval(
        _req(
            asset_id="tt_w31_install_02",
            utm_link=build_wizard_utm("tiktok", "installateur", "tt_w31_install_02"),
            caption="50 meter #installateur",
        ),
        tmp_path,
    )
    assert d.ok
    cal = set_slot_status(
        cal,
        asset_id="tt_w31_install_02",
        status="validated",
        request_id=d.request_id,
        pass_token=d.pass_token,
    )
    assert_publish_allowed(cal, "tt_w31_install_02")
