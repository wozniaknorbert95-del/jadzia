"""Unit tests for Facebook long-lived token exchange helper."""

from unittest.mock import MagicMock, patch

from deployment.exchange_fb_long_lived import exchange_long_lived_user_token


def test_exchange_skipped_without_app_credentials(monkeypatch):
    monkeypatch.delenv("FB_APP_ID", raising=False)
    monkeypatch.delenv("FB_APP_SECRET", raising=False)
    result = exchange_long_lived_user_token("short-token")
    assert result["status"] == "skipped"
    assert "FB_APP_ID" in result["message"]


def test_exchange_success(monkeypatch):
    monkeypatch.setenv("FB_APP_ID", "app123")
    monkeypatch.setenv("FB_APP_SECRET", "secret456")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = b'{"access_token":"long-user","expires_in":5184000}'
    mock_resp.json.return_value = {
        "access_token": "long-user",
        "expires_in": 5184000,
        "token_type": "bearer",
    }

    with patch("deployment.exchange_fb_long_lived.requests.get", return_value=mock_resp) as get:
        result = exchange_long_lived_user_token("short-token")

    assert result["status"] == "success"
    assert result["access_token"] == "long-user"
    assert result["expires_in"] == 5184000
    params = get.call_args.kwargs["params"]
    assert params["grant_type"] == "fb_exchange_token"
    assert params["fb_exchange_token"] == "short-token"
    assert params["client_id"] == "app123"


def test_exchange_http_error(monkeypatch):
    monkeypatch.setenv("FB_APP_ID", "app123")
    monkeypatch.setenv("FB_APP_SECRET", "secret456")

    mock_resp = MagicMock()
    mock_resp.status_code = 400
    mock_resp.content = b'{"error":{"message":"bad"}}'
    mock_resp.json.return_value = {"error": {"message": "bad"}}

    with patch("deployment.exchange_fb_long_lived.requests.get", return_value=mock_resp):
        result = exchange_long_lived_user_token("short-token")

    assert result["status"] == "error"
    assert "fb_exchange_token failed" in result["message"]


def test_exchange_missing_token():
    result = exchange_long_lived_user_token("")
    assert result["status"] == "error"
