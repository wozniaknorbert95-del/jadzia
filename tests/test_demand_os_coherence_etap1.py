"""ETAP 1 tool coherence — RBAC · GDrive honesty · GA4 UTM · fatigue · blog wire."""

from __future__ import annotations

import json
from pathlib import Path

from agent.commander.authz import has_scope
from agent.demand_os.agents.worker import CADENCE
from agent.demand_os.fatigue import fatigue_check
from agent.demand_os.ga4_adapter import fetch_wizard_starts_by_utm
from agent.demand_os.gdrive_cf import list_cf_assets
from agent.demand_os.rbac import SCOPE_ACT, SCOPE_READ, can_act, can_read
from agent.demand_os.utm_lock import build_wizard_utm
from agent.demand_os.validator import RULE_R9_DECOY_MENU, evaluate_publish_request
from agent.demand_os.publish_request import PublishRequest


def test_rbac_scopes():
    assert can_read(None) is True  # dowodca default
    assert can_act(None) is True
    viewer = {"role": "viewer", "sub": "v1"}
    assert has_scope(viewer, SCOPE_READ) is True
    assert has_scope(viewer, SCOPE_ACT) is False
    assert can_act(viewer) is False
    delegat = {"role": "delegat", "sub": "d1"}
    assert has_scope(delegat, SCOPE_ACT) is True


def test_gdrive_local_registry():
    out = list_cf_assets(limit=3)
    assert out["mode"] == "local_registry"
    assert out["ok"] is True
    assert len(out["assets"]) >= 1


def test_ga4_utm_fail_closed():
    out = fetch_wizard_starts_by_utm(days=7)
    assert out["ok"] is False
    assert out["mode"] == "stub"
    assert out["starts_by_utm"] == {}


def test_ga4_utm_csv(tmp_path: Path, monkeypatch):
    utm = build_wizard_utm("tiktok", "installateur", "tt_x")
    csv = tmp_path / "u.csv"
    csv.write_text(f"utm_link,starts\n{utm},2\n", encoding="utf-8")
    monkeypatch.setenv("DEMAND_OS_GA4_UTM_CSV", str(csv))
    out = fetch_wizard_starts_by_utm()
    assert out["ok"] is True
    assert out["starts_by_utm"][utm] == 2


def test_fatigue_and_decoy():
    f = fatigue_check("never_seen_asset_xyz")
    assert f["ok"] is True
    assert f["fatigue"] is False
    utm = build_wizard_utm("tiktok", "installateur", "tt_decoy")
    req = PublishRequest(
        asset_id="tt_decoy",
        channel="tiktok",
        icp_role="installateur",
        caption="Kies je pakket A of pakket B — #installateur",
        utm_link=utm,
        content_type="organic_post",
    )
    dec = evaluate_publish_request(req, log=False, emit_events=False)
    assert not dec.ok
    assert RULE_R9_DECOY_MENU in dec.fail_rules


def test_blog_pipeline_action():
    from agent.demand_os.agents.wave3 import run_wave3

    out = run_wave3("blog", action="pipeline", persist=False, calendar=False)
    assert out["role"] == "blog"
    assert "decision" in out["result"]
    assert out["live_ship"] is False


def test_hub_rbac_viewer_blocked(monkeypatch):
    import tools.demand_os_hub as hub

    monkeypatch.setenv("DEMAND_OS_ROLE", "viewer")
    # sync-db is act
    rc = hub.main(["sync-db", "--dry-run"])
    assert rc == 1
    monkeypatch.delenv("DEMAND_OS_ROLE", raising=False)
    rc2 = hub.main(["doctor"])
    assert rc2 == 0


def test_hub_rbac_viewer_blocked_run_due(monkeypatch):
    """S9: worker dispatcher (agents-run-due) is act-class — viewer must be denied."""
    import tools.demand_os_hub as hub

    monkeypatch.setenv("DEMAND_OS_ROLE", "viewer")
    rc = hub.main(["agents", "run-due", "--apply"])
    assert rc == 1, "viewer must not dispatch worker actions"
    rc_dry = hub.main(["agents", "run-due"])  # dry-run is still act-class (dispatch surface)
    assert rc_dry == 1


def test_doctor_surfaces_agents_staleness(monkeypatch, tmp_path):
    """S1: doctor aliases wave-check staleness — owner sees worker health via doctor."""
    from datetime import datetime, timedelta, timezone

    from agent.demand_os.doctor import run_doctor

    hb = tmp_path / "hb.json"
    monkeypatch.setenv("DEMAND_OS_AGENTS_HEARTBEAT", str(hb))

    fresh = datetime.now(timezone.utc).isoformat()
    hb.write_text(
        json.dumps(
            {r: {"role": r, "last_run_at": fresh, "run_count": 1} for r in CADENCE}
        ),
        encoding="utf-8",
    )
    rep = run_doctor()
    chk = next(c for c in rep.checks if c["name"] == "agents_staleness")
    assert chk["ok"] is True

    old = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    hb.write_text(
        json.dumps(
            {r: {"role": r, "last_run_at": old, "run_count": 1} for r in CADENCE}
        ),
        encoding="utf-8",
    )
    rep2 = run_doctor()
    chk2 = next(c for c in rep2.checks if c["name"] == "agents_staleness")
    assert chk2["ok"] is False
    assert "sales" in chk2["detail"]  # advisory, not blocking (wave-check is the hard gate)


def test_hub_engage_dry_reflects_go_env(tmp_path: Path, monkeypatch, capsys):
    import tools.demand_os_hub as hub

    pack = tmp_path / "set-now"
    pack.mkdir()
    (pack / "ALLOWLIST.json").write_text(
        json.dumps(
            {
                "targets": [
                    {
                        "id": "fb_g2",
                        "platform": "facebook",
                        "kind": "group_nl",
                        "name": "Demo group",
                        "status": "active",
                        "icp_role": "installateur",
                    }
                ],
                "max_groups": 1,
            }
        ),
        encoding="utf-8",
    )
    (pack / "ENGAGE-LOG.jsonl").write_text("", encoding="utf-8")
    monkeypatch.setenv("DEMAND_OS_SET_NOW", str(pack))
    monkeypatch.setenv("DEMAND_OS_MARKETING_HITL", "GO")

    rc = hub.main(
        [
            "engage-dry",
            "--target-id",
            "fb_g2",
            "--asset-id",
            "engage_go_test",
            "--icp-role",
            "installateur",
        ]
    )
    out = json.loads(capsys.readouterr().out)
    assert rc in (0, 1)
    assert out["marketing"] == "HITL_LIVE"
    if "live" in out:
        assert out["live"] is False
    else:
        assert "error" in out
