"""Tests for content calendar media intake (M1)."""

import os

import jwt as pyjwt
import pytest
from fastapi.testclient import TestClient

from api.app import create_app

JWT_SECRET_VALUE = "test-secret-content-media-32chars!!"


@pytest.fixture
def temp_db(monkeypatch):
    import tempfile

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setattr("agent.db.DB_PATH", path)
    import agent.db as db_mod

    if hasattr(db_mod._local, "conn") and db_mod._local.conn:
        db_mod._local.conn.close()
        db_mod._local.conn = None
    monkeypatch.setenv("JWT_SECRET", JWT_SECRET_VALUE)
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def client():
    return TestClient(create_app())


def _auth():
    token = pyjwt.encode(
        {"sub": "norbert", "role": "dowodca"},
        JWT_SECRET_VALUE,
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}


def test_create_image_entry_normalizes_gdrive(client, temp_db, monkeypatch):
    monkeypatch.setattr(
        "agent.media.gdrive.probe_media_url",
        lambda url: {"ok": True, "mime_type": "image/png", "media_url": url},
    )
    body = {
        "platform": "facebook",
        "title": "Test grafika",
        "body_nl": "NL caption voor test",
        "scheduled_at": "2026-07-15T09:00:00+00:00",
        "scheduled_publish_at": "2026-07-15T09:00:00+00:00",
        "content_type": "image",
        "media_url": "https://drive.google.com/file/d/abc123XYZ/view",
        "status": "draft",
    }
    r = client.post("/api/v1/content-calendar", json=body, headers=_auth())
    assert r.status_code == 200
    assert r.json()["sync_status"] == "success"

    listed = client.get("/api/v1/content-calendar", headers=_auth()).json()
    entry = listed["entries"][-1]
    assert "uc?export=download&id=abc123XYZ" in entry["media_url"]
    assert entry["content_type"] == "image"
    assert entry["media_source"] == "gdrive"


def test_create_image_requires_media_url(client, temp_db):
    body = {
        "platform": "facebook",
        "title": "Bez media",
        "body_nl": "Tekst",
        "scheduled_at": "2026-07-15T09:00:00+00:00",
        "content_type": "image",
    }
    r = client.post("/api/v1/content-calendar", json=body, headers=_auth())
    assert r.status_code == 400


def test_create_image_probe_fails_fast(client, temp_db, monkeypatch):
    monkeypatch.setattr(
        "agent.media.gdrive.probe_media_url",
        lambda url: {"ok": False, "error": "Plik niedostępny — sprawdź udostępnianie (każdy z linkiem)"},
    )
    body = {
        "platform": "facebook",
        "title": "Prywatny plik",
        "body_nl": "NL",
        "scheduled_at": "2026-07-15T09:00:00+00:00",
        "content_type": "image",
        "media_url": "https://drive.google.com/file/d/private/view",
        "status": "draft",
    }
    r = client.post("/api/v1/content-calendar", json=body, headers=_auth())
    assert r.status_code == 400
    assert "niedostępny" in r.json()["detail"].lower() or "udostępnianie" in r.json()["detail"].lower()


def test_publish_routes_photo(monkeypatch, client, temp_db):
    from agent.db import db_create_calendar_entry, db_update_calendar_entry

    eid, _ = db_create_calendar_entry({
        "platform": "facebook",
        "title": "Photo post",
        "body_nl": "NL",
        "scheduled_at": "2026-07-15T09:00:00+00:00",
        "status": "approved",
        "content_type": "image",
        "media_url": "https://drive.google.com/uc?export=download&id=abc",
        "media_source": "gdrive",
    })
    db_update_calendar_entry(int(eid), {"status": "approved"})

    called = {}

    def fake_publish(row):
        called["url"] = row.get("media_url")
        return {"status": "success", "post_id": "page_99"}

    monkeypatch.setenv("FB_PAGE_ID", "491325420727745")
    monkeypatch.setenv("FB_ACCESS_TOKEN", "test-token")
    monkeypatch.setattr("agent.commander.publish.publish_calendar_content", fake_publish)
    monkeypatch.setattr(
        "agent.commander.publish.db_update_calendar_entry_versioned",
        lambda *a, **k: (True, 2),
    )
    monkeypatch.setattr("agent.commander.publish.db_commander_increment_daily_actions", lambda: 1)
    monkeypatch.setattr("agent.commander.publish.append_audit", lambda **k: None)

    r = client.post(f"/api/v1/content-calendar/{eid}/publish", headers=_auth(), json={})
    assert r.status_code == 200
    assert called.get("url") == "https://drive.google.com/uc?export=download&id=abc"
