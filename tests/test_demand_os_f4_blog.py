"""Demand OS F4 — Blog ICP pipeline."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent.demand_os.blog_pipeline import (
    BlogPipelineError,
    generate_article,
    persist_article,
    run_pipeline,
    validate_article,
)
from agent.demand_os.utm_lock import validate_utm_url


def test_role_required():
    with pytest.raises(BlogPipelineError, match="icp_role required"):
        generate_article("")
    with pytest.raises(BlogPipelineError, match="generic"):
        generate_article("general")


def test_unknown_role_rejected():
    with pytest.raises(BlogPipelineError, match="allowlist"):
        generate_article("influencer")


def test_generate_installateur_utm_blog():
    art = generate_article("installateur")
    assert art.channel == "blog"
    assert art.icp_role == "installateur"
    assert "installateur" in art.title.lower() or "installateur" in art.body_md.lower()
    assert "bus" in art.body_md.lower() or "50" in art.body_md
    utm = validate_utm_url(art.utm_link)
    assert utm["ok"]
    assert utm["parts"]["channel"] == "blog"
    assert utm["parts"]["role"] == "installateur"
    assert utm["parts"]["asset_id"] == art.asset_id


def test_validate_pass(tmp_path: Path):
    art = generate_article("installateur", asset_id="blog_test_install_01")
    art, decision = validate_article(
        art,
        log=True,
        emit_events=False,
        log_path=tmp_path / "VALIDATOR-LOG.csv",
    )
    assert decision.ok, decision.fail_rules
    assert art.status == "validated"
    assert art.pass_token and art.pass_token.startswith("val_")
    assert "icp_role=installateur" in art.caption_for_validator()
    assert "#installateur" in art.caption_for_validator()


def test_pipeline_persists(tmp_path: Path, monkeypatch):
    # Avoid mutating repo CONTENT-CALENDAR during unit test
    from agent.demand_os import blog_pipeline as bp

    cal_path = tmp_path / "CONTENT-CALENDAR.json"
    cal_path.write_text(
        '{"version":1,"slots":[]}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "agent.demand_os.content_calendar.DEFAULT_CALENDAR_PATH",
        cal_path,
    )
    # content_calendar may use different constant name — patch load/save via drafts only
    result = run_pipeline(
        "installateur",
        asset_id="blog_pipe_install_01",
        persist=True,
        calendar=False,
        drafts_dir=tmp_path / "drafts",
        log=True,
        emit_events=False,
    )
    assert result["decision"]["decision"] == "PASS"
    assert Path(result["paths"]["json"]).exists()
    assert Path(result["paths"]["md"]).exists()
    data = Path(result["paths"]["json"]).read_text(encoding="utf-8")
    assert "installateur" in data
    assert "utm_source=blog" in data or "blog" in data


def test_persist_roundtrip(tmp_path: Path):
    art = generate_article("hovenier", asset_id="blog_test_hovenier_01")
    path = persist_article(art, drafts_dir=tmp_path)
    assert path.exists()
    assert (tmp_path / "blog_test_hovenier_01.md").exists()
