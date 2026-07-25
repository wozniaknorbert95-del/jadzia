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


def test_redact_secrets_strips_access_token():
    raw = "400 Bad Request for url: https://graph.facebook.com/v25.0/x?access_token=EAAsecret123&fields=id"
    assert "EAAsecret123" not in fb._redact_secrets(raw)
    assert "access_token=REDACTED" in fb._redact_secrets(raw)


def test_check_token_health_flags_user_content_scope():
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        "data": {
            "is_valid": True,
            "type": "PAGE",
            "expires_at": 0,
            "scopes": [
                "pages_manage_posts",
                "pages_read_engagement",
                "read_insights",
                "pages_read_user_content",
            ],
        }
    }
    with patch("agent.publishers.facebook.requests.get", return_value=mock_resp):
        health = fb.check_token_health()
    assert health["ok"] is True
    assert health["has_read_insights"] is True
    assert health["has_pages_read_user_content"] is True
    assert health["message_pl"] == "Token OK (Page)"


def test_check_token_health_warns_missing_user_content():
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        "data": {
            "is_valid": True,
            "type": "PAGE",
            "expires_at": 0,
            "scopes": ["pages_manage_posts", "read_insights"],
        }
    }
    with patch("agent.publishers.facebook.requests.get", return_value=mock_resp):
        health = fb.check_token_health()
    assert health["has_pages_read_user_content"] is False
    assert "pages_read_user_content" in health["message_pl"]


def test_fetch_post_organic_metrics_v25_media_view():
    eng = MagicMock()
    eng.raise_for_status = MagicMock()
    eng.json.return_value = {
        "id": "p1",
        "reactions": {"summary": {"total_count": 2}},
        "comments": {"summary": {"total_count": 1}},
        "shares": {"count": 0},
    }
    ins = MagicMock()
    ins.status_code = 200
    ins.json.return_value = {
        "data": [
            {"name": "post_total_media_view_unique", "values": [{"value": 100}]},
            {"name": "post_clicks", "values": [{"value": 3}]},
        ]
    }

    with patch(
        "agent.publishers.facebook.requests.get",
        side_effect=[eng, ins],
    ) as get:
        out = fb.fetch_post_organic_metrics("491325420727745_1")

    assert out["ok"] is True
    assert out["engagements"] == 3
    assert out["impressions"] == 100
    assert out["link_clicks"] == 3
    assert out["insights_ok"] is True
    metric_param = get.call_args_list[1].kwargs["params"]["metric"]
    assert "post_media_view" in metric_param
    assert "post_total_media_view_unique" in metric_param
    assert "post_media_view_unique" not in metric_param
    assert "post_impressions" not in metric_param


def test_delete_post_success():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"success": True}
    mock_resp.raise_for_status = MagicMock()

    with patch("agent.publishers.facebook.requests.delete", return_value=mock_resp):
        result = fb.delete_post("post123")

    assert result["status"] == "success"

