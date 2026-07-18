"""Enterprise Commander mobile login (COI-CMD-MOBILE-02)."""

import os
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
import pytest

from agent.commander.session_login import (
    exchange_login_code,
    mint_login_link,
    mint_session_jwt,
)
from agent.db import db_commander_get_login_code, get_connection

_TEST_JWT_SECRET = "test-mobile-02-secret-32bytes-min!!"


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
    get_connection()  # init schema
    monkeypatch.setenv("JWT_SECRET", _TEST_JWT_SECRET)
    monkeypatch.setattr(
        "agent.commander.session_login._jwt_secret",
        lambda: _TEST_JWT_SECRET,
    )
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


def test_mint_session_jwt_decodable(temp_db):
    token = mint_session_jwt(sub="42", role="dowodca", hours=1)
    payload = jwt.decode(token, _TEST_JWT_SECRET, algorithms=["HS256"])
    assert payload["sub"] == "42"
    assert payload["role"] == "dowodca"


def test_login_code_exchange_one_time(temp_db):
    link = mint_login_link(base_url="https://api.example", sub="99", role="dowodca")
    assert link["url"].startswith("https://api.example/commander/?code=")
    code = link["url"].split("code=", 1)[1]
    first = exchange_login_code(code)
    assert first is not None
    assert first["sub"] == "99"
    payload = jwt.decode(first["token"], _TEST_JWT_SECRET, algorithms=["HS256"])
    assert payload["role"] == "dowodca"
    second = exchange_login_code(code)
    assert second is None


def test_login_code_expired_rejected(temp_db):
    link = mint_login_link(base_url="https://api.example", sub="1")
    code = link["url"].split("code=", 1)[1]
    from agent.commander import session_login as sl

    code_hash = sl._hash_code(code)
    past = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    conn = get_connection()
    conn.execute(
        "UPDATE commander_login_codes SET expires_at = ? WHERE code_hash = ?",
        (past, code_hash),
    )
    conn.commit()
    assert exchange_login_code(code) is None
    assert db_commander_get_login_code(code_hash) is not None


def test_parse_commander_command():
    from api.telegram import parse_telegram_command

    assert parse_telegram_command("/commander", None) == ("commander", "")
    assert parse_telegram_command("/jwt", None) == ("commander", "")
    assert parse_telegram_command("/commander@MyBot", None) == ("commander", "")


def test_auth_exchange_http(temp_db):
    from fastapi.testclient import TestClient

    from api.app import create_app

    link = mint_login_link(base_url="https://api.example", sub="7")
    code = link["url"].split("code=", 1)[1]
    client = TestClient(create_app())
    r = client.post("/api/v1/commander/auth/exchange", json={"code": code})
    assert r.status_code == 200
    body = r.json()
    assert body.get("token")
    r2 = client.post("/api/v1/commander/auth/exchange", json={"code": code})
    assert r2.status_code == 401
