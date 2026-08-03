"""GDrive CF live connector — fail-closed, injectable transport, zero network."""

from __future__ import annotations

from unittest.mock import patch

import pytest

import agent.demand_os.gdrive_cf as gcf
from agent.demand_os.gdrive_cf import list_cf_assets, list_drive_folder


class _FakeResp:
    def __init__(self, status_code: int, payload: dict | None = None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload


def _live_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DEMAND_OS_GDRIVE_LIVE", "1")
    monkeypatch.setenv("GDRIVE_FOLDER_ID", "folder-123")
    monkeypatch.setenv("GDRIVE_CREDENTIALS_JSON", "{}")


def test_list_drive_folder_maps_response():
    calls = {}

    def fake_get(url, *, headers, params, timeout):
        calls["url"] = url
        calls["headers"] = headers
        calls["params"] = params
        return _FakeResp(
            200,
            {
                "files": [
                    {
                        "id": "f1",
                        "name": "tt_w32_install_01.mp4",
                        "mimeType": "video/mp4",
                        "modifiedTime": "2026-08-03T10:00:00Z",
                    }
                ]
            },
        )

    out = list_drive_folder("folder-123", limit=5, token="t", http_get=fake_get)
    assert out["ok"] is True
    assert out["mode"] == "live"
    assert out["files"][0]["gdrive_file_id"] == "f1"
    assert out["files"][0]["mime_type"] == "video/mp4"
    assert calls["headers"]["Authorization"] == "Bearer t"
    assert "'folder-123' in parents" in calls["params"]["q"]


def test_list_drive_folder_http_error_fail_closed():
    def fake_get(url, *, headers, params, timeout):
        return _FakeResp(403)

    out = list_drive_folder("folder-123", token="t", http_get=fake_get)
    assert out["ok"] is False
    assert out["mode"] == "live_error"
    assert "403" in out["error"]


def test_list_drive_folder_transport_raises_fail_closed():
    def fake_get(url, *, headers, params, timeout):
        raise TimeoutError("boom")

    out = list_drive_folder("folder-123", token="t", http_get=fake_get)
    assert out["ok"] is False
    assert out["mode"] == "live_error"
    assert "TimeoutError" in out["error"]


def test_bad_inline_json_never_raises(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("GDRIVE_CREDENTIALS_JSON", "{not-json")
    monkeypatch.delenv("GA4_CREDENTIALS_JSON", raising=False)
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    out = list_drive_folder("folder-123")
    assert out["ok"] is False
    assert out["mode"] in ("live_error", "missing_config")


def test_list_cf_assets_live_ok_maps_assets(monkeypatch: pytest.MonkeyPatch):
    _live_env(monkeypatch)
    with patch.object(
        gcf,
        "list_drive_folder",
        return_value={
            "ok": True,
            "mode": "live",
            "files": [
                {
                    "gdrive_file_id": "f1",
                    "name": "tt_w32_install_01.mp4",
                    "mime_type": "video/mp4",
                    "modified": "2026-08-03T10:00:00Z",
                }
            ],
            "error": "",
        },
    ):
        out = list_cf_assets(limit=5)
    assert out["ok"] is True
    assert out["mode"] == "live"
    assert out["assets"][0]["asset_id"] == "tt_w32_install_01"
    assert out["assets"][0]["gdrive_file_id"] == "f1"
    assert out["assets"][0]["source"] == "gdrive_live"


def test_list_cf_assets_live_error_keeps_local_fallback(monkeypatch: pytest.MonkeyPatch):
    _live_env(monkeypatch)
    with patch.object(
        gcf,
        "list_drive_folder",
        return_value={"ok": False, "mode": "live_error", "files": [], "error": "http 500"},
    ):
        out = list_cf_assets(limit=5)
    assert out["ok"] is False
    assert out["mode"] == "live_error"
    assert out["fallback"]["mode"] in ("local_registry", "missing_registry")


def test_list_cf_assets_live_without_config_stays_stub(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DEMAND_OS_GDRIVE_LIVE", "1")
    monkeypatch.delenv("GDRIVE_FOLDER_ID", raising=False)
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    monkeypatch.delenv("GA4_CREDENTIALS_JSON", raising=False)
    monkeypatch.delenv("GDRIVE_CREDENTIALS_JSON", raising=False)
    out = list_cf_assets(limit=5)
    assert out["ok"] is False
    assert out["mode"] == "stub"
