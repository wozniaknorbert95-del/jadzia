"""Unit tests for widget Wizard CTA + optional durable lead."""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agent.customer_agent import (
    _cta_effective_score,
    _cta_intent_is_high,
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
    assert _cta_effective_score(65, 30) == 65
    assert _cta_effective_score(20, 45) == 45
    assert _cta_intent_is_high("high", "medium") is True
    assert _cta_intent_is_high("low", "medium") is False
    assert _should_attach_cta(30, "low", ai_intent="high", scorer_intent="medium") is True
    assert _should_attach_cta(30, "low", ai_intent="low", scorer_intent="medium") is False


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
async def test_cta_when_ai_score_beats_low_scorer(monkeypatch):
    """Regression: AI 65/high must CTA even when LeadScorer returns 30/medium."""
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
                '{"reply":"Interessant","lead":{"score":65,"intent":"high",'
                '"category":"wycena","reason":"buy signal"},"suggested_sku":"CS-SET-PRO-ZZP",'
                '"vehicle":"caddy","consent_lead_storage":false}'
            )
        )
    ]
    mock_client.messages.create = AsyncMock(return_value=mock_msg)

    with patch("agent.customer_agent.client", mock_client):
        with patch("agent.customer_agent.Thread"):
            with patch("agent.customer_agent.LeadScorer") as mock_scorer_cls:
                mock_scorer_cls.return_value.compute.return_value = {
                    "lead_score": 30,
                    "intent": "medium",
                    "category": "informacja",
                    "reason": "scorer below CTA alone",
                }
                result = await process_customer_message(
                    "sess-cta-gap",
                    "Hallo, ik kijk even rond",
                )

    assert result["wizard_deeplink"]
    assert "highlight=CS-SET-PRO-ZZP" in result["wizard_deeplink"]
    assert result["cta_sku"] == "CS-SET-PRO-ZZP"
    assert result.get("lead_score") == 30
    assert result["lead"]["score"] == 65
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.mark.asyncio
async def test_cta_when_only_ai_intent_high(monkeypatch):
    """AI intent high alone attaches CTA even if both scores are below 40."""
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
                '{"reply":"Ok","lead":{"score":10,"intent":"high",'
                '"category":"wycena","reason":"urgent"},"suggested_sku":"MA-005",'
                '"vehicle":"transporter","consent_lead_storage":false}'
            )
        )
    ]
    mock_client.messages.create = AsyncMock(return_value=mock_msg)

    with patch("agent.customer_agent.client", mock_client):
        with patch("agent.customer_agent.Thread"):
            with patch("agent.customer_agent.LeadScorer") as mock_scorer_cls:
                mock_scorer_cls.return_value.compute.return_value = {
                    "lead_score": 20,
                    "intent": "low",
                    "category": "informacja",
                    "reason": "low",
                }
                result = await process_customer_message(
                    "sess-cta-intent",
                    "alleen kijken",
                )

    assert result["wizard_deeplink"]
    assert "voertuig=transporter" in result["wizard_deeplink"]
    assert result["cta_sku"] == "MA-005"
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.mark.asyncio
async def test_no_cta_when_both_scores_low_and_intent_not_high(monkeypatch):
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
                '{"reply":"Hallo","lead":{"score":10,"intent":"low",'
                '"category":"informacja","reason":"greet"},"suggested_sku":null,'
                '"vehicle":null,"consent_lead_storage":false}'
            )
        )
    ]
    mock_client.messages.create = AsyncMock(return_value=mock_msg)

    with patch("agent.customer_agent.client", mock_client):
        with patch("agent.customer_agent.Thread"):
            with patch("agent.customer_agent.LeadScorer") as mock_scorer_cls:
                mock_scorer_cls.return_value.compute.return_value = {
                    "lead_score": 15,
                    "intent": "low",
                    "category": "informacja",
                    "reason": "low",
                }
                result = await process_customer_message("sess-no-cta", "hoi")

    assert result.get("wizard_deeplink") is None
    assert result.get("cta_sku") is None
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
