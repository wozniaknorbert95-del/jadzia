"""Unit tests — INSPIRE offerte concierge."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from agent.inspire.offerte_service import create_offerte_request


def _valid_body(session_id: str = "sess-1") -> dict:
    return {
        "session_id": session_id,
        "locale": "nl-NL",
        "contact": {
            "email": "klant@voorbeeld.nl",
            "telefoon": "+31612345678",
            "consent_offerte": True,
        },
        "selection": {
            "variant": "standard",
            "sku": "MA-005",
            "product_naam": "Magneetset",
            "price_from_eur": 129,
            "mockup_url": "https://example/mock.png",
        },
        "brief_partial": {"bedrijfsnaam": "Test BV"},
        "generate_meta": {},
    }


def test_validate_rejects_missing_consent():
    body = _valid_body()
    body["contact"]["consent_offerte"] = False
    with pytest.raises(ValueError, match="consent"):
        create_offerte_request(body)


@patch("agent.inspire.offerte_service.db_offerte_find_recent", return_value=None)
@patch("agent.inspire.offerte_service.db_offerte_insert")
@patch("agent.db.db_offerte_update_notify")
@patch("agent.inspire.offerte_service._send_delegat_email", return_value=True)
@patch("agent.inspire.offerte_service.Thread")
def test_create_offerte_success(
    mock_thread,
    mock_email,
    mock_update,
    mock_insert,
    mock_dup,
):
    mock_thread.return_value = MagicMock()
    result = create_offerte_request(_valid_body(), client_ip="127.0.0.1")
    assert result["ok"] is True
    assert result["offerte_request_id"].startswith("off-")
    mock_insert.assert_called_once()


@patch("agent.inspire.offerte_service.db_offerte_find_recent", return_value=None)
@patch("agent.inspire.offerte_service.db_offerte_insert")
@patch("agent.db.db_offerte_update_notify")
@patch("agent.inspire.offerte_service._send_delegat_email", return_value=True)
@patch("agent.inspire.offerte_service.Thread")
def test_create_offerte_analytics_fail_safe(
    mock_thread,
    mock_email,
    mock_update,
    mock_insert,
    mock_dup,
    monkeypatch: pytest.MonkeyPatch,
):
    """T-012 analytics hook must never break offerte creation (best-effort)."""
    mock_thread.return_value = MagicMock()
    # no INSPIRE_REPO_PATH → silent no-op
    monkeypatch.delenv("INSPIRE_REPO_PATH", raising=False)
    result = create_offerte_request(_valid_body(), client_ip="127.0.0.1")
    assert result["ok"] is True
    # bogus repo path → handler import fails → warning, still ok
    monkeypatch.setenv("INSPIRE_REPO_PATH", "C:/nonexistent-inspire-repo")
    result2 = create_offerte_request(_valid_body(session_id="sess-2"), client_ip="127.0.0.1")
    assert result2["ok"] is True


@patch("agent.inspire.offerte_service.db_offerte_find_recent")
def test_duplicate_returns_existing(mock_dup):
    mock_dup.return_value = {"id": "off-20260727-abc123"}
    result = create_offerte_request(_valid_body())
    assert result["duplicate"] is True
    assert result["offerte_request_id"] == "off-20260727-abc123"
