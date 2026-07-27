"""Unit tests for agent.publishers.tiktok (TT-PUB-01)."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from agent.publishers import tiktok as tt
from agent.publishers.calendar_publish import publish_calendar_content


@pytest.fixture(autouse=True)
def tt_env(monkeypatch):
    monkeypatch.setenv("TIKTOK_ACCESS_TOKEN", "act.test-token")
    monkeypatch.setenv("TIKTOK_DEFAULT_PRIVACY", "SELF_ONLY")


def test_is_tiktok_configured_true():
    assert tt.is_tiktok_configured() is True


def test_is_tiktok_configured_false(monkeypatch):
    monkeypatch.delenv("TIKTOK_ACCESS_TOKEN", raising=False)
    assert tt.is_tiktok_configured() is False


def test_publish_video_success():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = b"{}"
    mock_resp.json.return_value = {
        "error": {"code": "ok"},
        "data": {"publish_id": "v_pub_123"},
    }
    mock_resp.raise_for_status = MagicMock()

    with patch("agent.publishers.tiktok.requests.post", return_value=mock_resp) as post:
        result = tt.publish_video(
            "Hook NL",
            "https://cdn.example.com/tt_hook.mp4",
        )

    assert result["status"] == "success"
    assert result["post_id"] == "v_pub_123"
    assert result["publish_id"] == "v_pub_123"
    body = post.call_args.kwargs["json"]
    assert body["source_info"]["source"] == "PULL_FROM_URL"
    assert body["post_info"]["privacy_level"] == "SELF_ONLY"
    assert "Authorization" in post.call_args.kwargs["headers"]


def test_publish_video_rejects_non_https():
    result = tt.publish_video("x", "http://insecure.example/a.mp4")
    assert result["status"] == "error"
    assert "https" in result["error"].lower()


def test_publish_video_api_error():
    mock_resp = MagicMock()
    mock_resp.status_code = 403
    mock_resp.content = b"{}"
    mock_resp.text = '{"error":{"code":"url_ownership_unverified","message":"bad domain"}}'
    mock_resp.json.return_value = {
        "error": {"code": "url_ownership_unverified", "message": "bad domain"},
    }

    with patch("agent.publishers.tiktok.requests.post", return_value=mock_resp):
        result = tt.publish_video("x", "https://cdn.example.com/a.mp4")

    assert result["status"] == "error"
    assert "bad domain" in result["error"]


def test_publish_video_http_exception():
    err = requests.HTTPError("400 Bad Request")
    err.response = MagicMock(text="OAuth")
    with patch("agent.publishers.tiktok.requests.post", side_effect=err):
        result = tt.publish_video("x", "https://cdn.example.com/a.mp4")
    assert result["status"] == "error"


def test_calendar_publish_routes_tiktok_video():
    row = {
        "platform": "tiktok",
        "content_type": "video",
        "body_nl": "Caption NL",
        "media_url": "https://cdn.example.com/tt.mp4",
    }
    with patch(
        "agent.publishers.calendar_publish.tt.publish_video",
        return_value={"status": "success", "post_id": "p1"},
    ) as pub:
        result = publish_calendar_content(row)
    assert result["status"] == "success"
    pub.assert_called_once_with("Caption NL", "https://cdn.example.com/tt.mp4")


def test_calendar_publish_tiktok_rejects_text():
    result = publish_calendar_content(
        {
            "platform": "tiktok",
            "content_type": "text",
            "body_nl": "hi",
        }
    )
    assert result["status"] == "error"
    assert "video" in result["error"].lower()


def test_redact_bearer():
    assert "REDACTED" in tt._redact_secrets("Bearer act.secret123ABC")
    assert "act.secret123ABC" not in tt._redact_secrets("Bearer act.secret123ABC")
