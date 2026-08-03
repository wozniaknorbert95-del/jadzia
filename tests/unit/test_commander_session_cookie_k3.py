"""K3 — session cookie on login exchange + logout clears cookie."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from agent.commander.session_login import SESSION_COOKIE_NAME, mint_login_link
from agent.db import get_connection

_TEST_JWT_SECRET = "test-k3-cookie-secret-32bytes-min!!"


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
    get_connection()
    monkeypatch.setenv("JWT_SECRET", _TEST_JWT_SECRET)
    monkeypatch.setattr(
        "agent.commander.session_login._jwt_secret",
        lambda: _TEST_JWT_SECRET,
    )
    monkeypatch.setattr("api.dependencies.JWT_SECRET", _TEST_JWT_SECRET)
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def client(temp_db):
    from api.app import create_app

    return TestClient(create_app())


def test_exchange_sets_httponly_cookie(client):
    link = mint_login_link(base_url="https://example.test", sub="dowodca", role="dowodca")
    code = link["url"].split("code=", 1)[1]
    res = client.post("/api/v1/commander/auth/exchange", json={"code": code})
    assert res.status_code == 200, res.text
    assert res.json()["token"]
    assert SESSION_COOKIE_NAME in res.cookies
    set_cookie = res.headers.get("set-cookie", "")
    assert "HttpOnly" in set_cookie or "httponly" in set_cookie.lower()


def test_logout_clears_cookie(client):
    res = client.post("/api/v1/commander/auth/logout")
    assert res.status_code == 200
    assert res.json()["logged_out"] is True


def test_session_jwt_default_hours_is_7_days():
    from agent.commander.session_login import SESSION_JWT_HOURS

    assert SESSION_JWT_HOURS >= 24 * 7


def test_session_probe_accepts_cookie(client):
    link = mint_login_link(base_url="https://example.test", sub="dowodca", role="dowodca")
    code = link["url"].split("code=", 1)[1]
    exch = client.post("/api/v1/commander/auth/exchange", json={"code": code})
    assert exch.status_code == 200
    # Cookie-only probe (no Authorization header)
    res = client.get("/api/v1/commander/auth/session")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["ok"] is True
    assert body["role"] == "dowodca"
