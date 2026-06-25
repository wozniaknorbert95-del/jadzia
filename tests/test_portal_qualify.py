"""Tests for POST /api/v1/portal/qualify — qualification funnel."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from agent.portal_qualification_agent import clear_qualification_sessions_for_tests
from api.app import create_app


@pytest.fixture(autouse=True)
def clear_sessions():
    clear_qualification_sessions_for_tests()
    yield
    clear_qualification_sessions_for_tests()


@pytest.fixture
def client():
    return TestClient(create_app())


def _post(client, session_id: str, message: str, step: str | None = None, consent: bool = False):
    payload = {"session_id": session_id, "message": message, "consent_lead_storage": consent}
    if step is not None:
        payload["step"] = step
    return client.post("/api/v1/portal/qualify", json=payload)


def test_portal_qualify_greeting_advances_to_industry(client):
    res = _post(client, "sess-1", "Hoi", step="greeting")
    assert res.status_code == 200
    data = res.json()
    assert data["schema_version"] == "qual_v1"
    assert data["step_next"] == "q1_industry"
    assert len(data["ui_suggestions"]) >= 6
    assert "branche" in data["reply"].lower()


def test_portal_qualify_full_funnel_to_groeier(client):
    sid = "sess-funnel-groeier"
    steps = [
        ("greeting", "Hoi"),
        ("q1_industry", "bouw"),
        ("q2_goal", "voertuig reclame"),
        ("q3_vehicle", "bedrijfsbus"),
        ("q4_budget", "300-700"),
    ]
    last = None
    for step, msg in steps:
        last = _post(client, sid, msg, step=step).json()

    assert last["step_next"] == "done"
    assert last["recommended_preset_id"] == "groeier"
    assert last["cta"]["type"] == "wizard"
    assert "preset=groeier" in last["wizard_deep_link"]


def test_portal_qualify_flota_whatsapp_cta(client):
    sid = "sess-flota"
    flow = [
        ("greeting", "Hoi"),
        ("q1_industry", "techniek"),
        ("q2_goal", "vloot"),
        ("q3_vehicle", "vloot"),
        ("q4_budget", "700+"),
    ]
    last = None
    for step, msg in flow:
        last = _post(client, sid, msg, step=step).json()

    assert last["recommended_preset_id"] == "professional-flota"
    assert last["cta"]["type"] == "whatsapp"
    assert last["wizard_deep_link"] is None


def test_portal_qualify_invalid_slot_reasks(client):
    sid = "sess-invalid"
    _post(client, sid, "Hoi", step="greeting")
    res = _post(client, sid, "xyz nonsense", step="q1_industry")
    data = res.json()
    assert data["step_next"] == "q1_industry"
    assert "Kun je een van de opties kiezen" in data["reply"]


def test_portal_qualify_consent_flag_on_recommend(client):
    sid = "sess-consent"
    with patch("agent.portal_qualification_agent.save_portal_qual_lead", return_value=True) as mock_save:
        for step, msg in [
            ("greeting", "bouw"),
            ("q2_goal", "meer klanten"),
            ("q3_vehicle", "geen"),
        ]:
            _post(client, sid, msg, step=step)

        last = _post(client, sid, "onder 300", step="q4_budget", consent=True).json()
        assert last["recommended_preset_id"] == "starter-zzp"
        assert last["lead_saved"] is True
        mock_save.assert_called_once()


def test_portal_qualify_no_consent_no_lead_save(client):
    sid = "sess-no-consent"
    with patch("agent.portal_qualification_agent.save_portal_qual_lead") as mock_save:
        for step, msg in [
            ("greeting", "bouw"),
            ("q2_goal", "meer klanten"),
            ("q3_vehicle", "geen"),
        ]:
            _post(client, sid, msg, step=step)

        last = _post(client, sid, "onder 300", step="q4_budget", consent=False).json()
        assert last["recommended_preset_id"] == "starter-zzp"
        assert last["lead_saved"] is False
        mock_save.assert_not_called()


def test_portal_qualify_done_step_no_crash(client):
    sid = "sess-done"
    for step, msg in [
        ("greeting", "bouw"),
        ("q2_goal", "meer klanten"),
        ("q3_vehicle", "bus"),
        ("q4_budget", "300-700"),
    ]:
        _post(client, sid, msg, step=step)

    res = _post(client, sid, "nog een vraag", step="done")
    assert res.status_code == 200
    data = res.json()
    assert data["step_next"] == "done"
    assert "advies" in data["reply"].lower()


def test_portal_qualify_server_owns_step(client):
    """Client sends stale step; server session advances correctly."""
    sid = "sess-server-step"
    _post(client, sid, "Hoi", step="greeting")
    # Client wrongly thinks still greeting while server is at q1_industry
    res = _post(client, sid, "bouw", step="greeting").json()
    assert res["step_next"] == "q2_goal"
    assert res["qualification_profile"]["industry"] == "bouw"
