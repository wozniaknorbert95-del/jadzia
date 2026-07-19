"""Tests for Facebook token health preflight."""

import os
from unittest.mock import MagicMock, patch

import pytest

from agent.publishers.facebook import check_token_health, parse_publish_error


def test_check_token_health_not_configured(monkeypatch):
    monkeypatch.delenv("FB_PAGE_ID", raising=False)
    monkeypatch.delenv("FB_ACCESS_TOKEN", raising=False)
    result = check_token_health()
    assert result["ok"] is False
    assert result["configured"] is False


def test_check_token_health_page_ok(monkeypatch):
    monkeypatch.setenv("FB_PAGE_ID", "491325420727745")
    monkeypatch.setenv("FB_ACCESS_TOKEN", "page-token")

    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        "data": {
            "is_valid": True,
            "type": "PAGE",
            "expires_at": 2000000000,
            "scopes": [
                "pages_manage_posts",
                "pages_read_engagement",
                "read_insights",
            ],
        }
    }

    with patch("agent.publishers.facebook.requests.get", return_value=mock_resp):
        result = check_token_health()

    assert result["ok"] is True
    assert result["token_type"] == "PAGE"
    assert result["days_left"] is not None
    assert result["has_read_insights"] is True
    assert "read_insights" in result["scopes"]


def test_check_token_health_missing_read_insights(monkeypatch):
    monkeypatch.setenv("FB_PAGE_ID", "491325420727745")
    monkeypatch.setenv("FB_ACCESS_TOKEN", "page-token")

    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        "data": {
            "is_valid": True,
            "type": "PAGE",
            "expires_at": 0,
            "scopes": ["pages_manage_posts", "pages_read_engagement"],
        }
    }

    with patch("agent.publishers.facebook.requests.get", return_value=mock_resp):
        result = check_token_health()

    assert result["ok"] is True
    assert result["has_read_insights"] is False
    assert "read_insights" in result["message_pl"]


def test_check_token_health_user_token_warns(monkeypatch):
    monkeypatch.setenv("FB_PAGE_ID", "491325420727745")
    monkeypatch.setenv("FB_ACCESS_TOKEN", "user-token")

    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        "data": {"is_valid": True, "type": "USER", "expires_at": 2000000000}
    }

    with patch("agent.publishers.facebook.requests.get", return_value=mock_resp):
        result = check_token_health()

    assert result["ok"] is False
    assert "Page Token" in result["message_pl"]
