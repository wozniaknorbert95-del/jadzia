"""Unit tests for widget Wizard CTA + optional durable lead."""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agent.customer_agent import (
    _extract_email,
    _has_consent,
    _should_attach_cta,
    build_widget_wizard_deeplink,
    process_customer_message,
)


def test_build_widget_wizard_deeplink():
    url = build_widget_wizard_deeplink("caddy", "MA-005")
    assert "zzpackage.flexgrafik.nl/wizard/" in url
    assert "voertuig=caddy" in url
    assert "highlight=MA-005" in url


def test_extract_email_and_consent():
    assert _extract_email("Mail me: jan@bouw.nl thanks") == "jan@bouw.nl"
    assert _has_consent("ja mag bewaren", {}) is True
    assert _has_consent("hello", {"consent_lead_storage": True}) is True
    assert _has_consent("hello", {}) is False


def test_should_attach_cta_threshold():
    assert _should_attach_cta(40, "low") is True
    assert _should_attach_cta(10, "high") is True
    assert _should_attach_cta(10, "low") is False


@pytest.mark.asyncio
async def test_process_customer_message_adds_deeplink(monkeypatch):
    import tempfile

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setattr("agent.db.DB_PATH", path)
    import agent.db as db_mod

    if hasattr(db_mod._local, "conn") and db_mod._local.conn:
        db_mod._local.conn.close()
        db_mod._local.conn = None

    mock_client = MagicMock()
    mock_msg = MagicMock()
    mock_msg.content = [
        MagicMock(
            text=(
                '{"reply":"Ga naar de Wizard","lead":{"score":70,"intent":"high",'
                '"category":"wycena","reason":"buy"},"suggested_sku":"MA-005",'
                '"vehicle":"caddy","consent_lead_storage":false}'
            )
        )
    ]
    mock_client.messages.create = AsyncMock(return_value=mock_msg)

    with patch("agent.customer_agent.client", mock_client):
        with patch("agent.customer_agent.Thread"):
            result = await process_customer_message("sess-1", "Ik wil een offerte")

    assert result["wizard_deeplink"]
    assert "highlight=MA-005" in result["wizard_deeplink"]
    assert result["cta_sku"] == "MA-005"
    assert result.get("lead_id") is None
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.mark.asyncio
async def test_process_customer_message_persists_lead_with_email_consent(monkeypatch):
    import tempfile

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setattr("agent.db.DB_PATH", path)
    import agent.db as db_mod

    if hasattr(db_mod._local, "conn") and db_mod._local.conn:
        db_mod._local.conn.close()
        db_mod._local.conn = None

    mock_client = MagicMock()
    mock_msg = MagicMock()
    mock_msg.content = [
        MagicMock(
            text=(
                '{"reply":"Bedankt","lead":{"score":80,"intent":"high",'
                '"category":"wycena","reason":"buy"},"suggested_sku":null,'
                '"vehicle":null,"consent_lead_storage":true}'
            )
        )
    ]
    mock_client.messages.create = AsyncMock(return_value=mock_msg)

    with patch("agent.customer_agent.client", mock_client):
        with patch("agent.customer_agent.Thread"):
            result = await process_customer_message(
                "sess-2",
                "Bel me op jan.demand@test.nl akkoord toestemming",
            )

    assert result.get("lead_id")
    from agent.db import db_get_lead_by_email

    lead = db_get_lead_by_email("jan.demand@test.nl")
    assert lead is not None
    assert lead["source"] == "web"
    try:
        os.unlink(path)
    except OSError:
        pass
