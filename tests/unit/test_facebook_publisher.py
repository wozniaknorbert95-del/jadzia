"""Unit tests for agent.publishers.facebook (INT-011)."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from agent.publishers import facebook as fb


@pytest.fixture(autouse=True)
def fb_env(monkeypatch):
    monkeypatch.setenv("FB_PAGE_ID", "491325420727745")
    monkeypatch.setenv("FB_ACCESS_TOKEN", "test-page-token")


def test_is_facebook_configured_true():
    assert fb.is_facebook_configured() is True


def test_is_facebook_configured_false(monkeypatch):
    monkeypatch.delenv("FB_ACCESS_TOKEN", raising=False)
    assert fb.is_facebook_configured() is False


def test_publish_post_success():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"id": "491325420727745_123456"}
    mock_resp.raise_for_status = MagicMock()

    with patch("agent.publishers.facebook.requests.post", return_value=mock_resp) as post:
        result = fb.publish_post("Jadzia COI test")

    assert result["status"] == "success"
    assert result["post_id"] == "491325420727745_123456"
    post.assert_called_once()
    call_kwargs = post.call_args.kwargs
    assert call_kwargs["data"]["message"] == "Jadzia COI test"
    assert "access_token" in call_kwargs["data"]


def test_publish_post_scheduled():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"id": "491325420727745_999"}
    mock_resp.raise_for_status = MagicMock()

    with patch("agent.publishers.facebook.requests.post", return_value=mock_resp) as post:
        result = fb.publish_post("Scheduled post", scheduled_publish_time=1700000000)

    assert result["status"] == "success"
    assert result["scheduled"] is True
    assert post.call_args.kwargs["data"]["published"] == "false"


def test_publish_post_http_error():
    mock_resp = MagicMock()
    mock_resp.text = "OAuthException"
    err = requests.HTTPError("400 Bad Request")
    err.response = mock_resp

    with patch(
        "agent.publishers.facebook.requests.post",
        side_effect=err,
    ):
        result = fb.publish_post("fail")

    assert result["status"] == "error"
    assert "400" in result["error"]


def test_publish_post_missing_config(monkeypatch):
    monkeypatch.delenv("FB_PAGE_ID", raising=False)
    with pytest.raises(RuntimeError, match="FB_PAGE_ID"):
        fb.publish_post("x")


def test_publish_photo_success():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"post_id": "491325420727745_888", "id": "photo123"}
    mock_resp.raise_for_status = MagicMock()

    with patch("agent.publishers.facebook.requests.post", return_value=mock_resp) as post:
        result = fb.publish_photo("Caption NL", "https://drive.google.com/uc?export=download&id=x")

    assert result["status"] == "success"
    assert result["post_id"] == "491325420727745_888"
    assert post.call_args.kwargs["data"]["url"].startswith("https://drive.google.com")


def test_publish_video_success():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"id": "491325420727745_777"}
    mock_resp.raise_for_status = MagicMock()

    video_url = "https://drive.google.com/uc?export=download&id=vid123"
    with patch("agent.publishers.facebook.requests.post", return_value=mock_resp) as post:
        result = fb.publish_video("Video caption NL", video_url)

    assert result["status"] == "success"
    assert result["post_id"] == "491325420727745_777"
    data = post.call_args.kwargs["data"]
    assert data["description"] == "Video caption NL"
    assert data["file_url"] == video_url
    assert post.call_args.kwargs["timeout"] == 120


def test_publish_video_http_error():
    mock_resp = MagicMock()
    mock_resp.text = "Video OAuthException"
    err = requests.HTTPError("400 Bad Request")
    err.response = mock_resp

    with patch("agent.publishers.facebook.requests.post", side_effect=err):
        result = fb.publish_video("fail", "https://example.com/v.mp4")

    assert result["status"] == "error"
    assert "400" in result["error"]


def test_parse_publish_error_video():
    details = '{"error":{"message":"Invalid file_url for video"}}'
    msg = fb.parse_publish_error({"status": "error", "details": details})
    assert "wideo" in msg.lower()


def test_check_post_status_success():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"id": "post123", "message": "hello"}
    mock_resp.raise_for_status = MagicMock()

    with patch("agent.publishers.facebook.requests.get", return_value=mock_resp):
        result = fb.check_post_status("post123")

    assert result["status"] == "success"
    assert result["data"]["message"] == "hello"


def test_delete_post_success():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"success": True}
    mock_resp.raise_for_status = MagicMock()

    with patch("agent.publishers.facebook.requests.delete", return_value=mock_resp):
        result = fb.delete_post("post123")

    assert result["status"] == "success"
