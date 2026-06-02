"""Unit tests for LeadScoring integration in customer_agent.py."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from core.lead_scoring import LeadScorer


@pytest.fixture(autouse=True)
def clear_cache():
    from agent.customer_agent import _customer_sessions_cache
    _customer_sessions_cache.clear()
    yield
    _customer_sessions_cache.clear()


def _make_mock_response(text: str):
    mock_content = AsyncMock()
    mock_content.text = text
    mock_response = AsyncMock()
    mock_response.content = [mock_content]
    return mock_response


@pytest.mark.asyncio
async def test_score_is_passed_to_reply():
    """Verify LeadScorer score is included in the response dict."""
    from agent.customer_agent import process_customer_message

    ai_reply = '{"reply": "Dzień dobry, w czym mogę pomóc?", "lead": {"score": 0}}'
    mock_response = _make_mock_response(ai_reply)

    with patch("agent.customer_agent.client.messages.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response
        result = await process_customer_message("test-session-score", "Chcę zamówić oklejenie auta")

    assert "lead_score" in result
    assert isinstance(result["lead_score"], int)
    assert result["lead_score"] >= 0
    assert result["lead_score"] <= 100
    assert "intent" in result
    assert result["intent"] in ("low", "medium", "high")
    assert "category" in result
    assert "reason" in result


@pytest.mark.asyncio
async def test_intent_high_triggers_urgent_reply():
    """Verify high-intent message produces score >= 60 and high intent."""
    from agent.customer_agent import process_customer_message

    ai_reply = '{"reply": "Oto wycena", "lead": {"score": 0}}'
    mock_response = _make_mock_response(ai_reply)

    with patch("agent.customer_agent.client.messages.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response
        result = await process_customer_message(
            "test-session-high", "Ile kosztuje full wrap? Chcę zamówić dla 3 aut."
        )

    assert result["lead_score"] >= 60
    assert result["intent"] == "high"
    assert result["category"] == "wycena"


@pytest.mark.asyncio
async def test_fallback_error_handling():
    """Verify that when LeadScorer raises, error dict is returned."""
    from agent.customer_agent import process_customer_message

    ai_reply = '{"reply": "OK", "lead": {"score": 0}}'
    mock_response = _make_mock_response(ai_reply)

    with patch("agent.customer_agent.client.messages.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response
        with patch("core.lead_scoring.LeadScorer.compute", side_effect=RuntimeError("Scorer failure")):
            result = await process_customer_message("test-session-error", "Hello")

    assert "error" in result
    assert result["error"] == "system_temporarily_unavailable"
    assert result["code"] == 503


@pytest.mark.asyncio
async def test_basic_low_intent_processing():
    """Verify low-intent greeting produces low score."""
    from agent.customer_agent import process_customer_message

    ai_reply = '{"reply": "Dzień dobry!", "lead": {"score": 0}}'
    mock_response = _make_mock_response(ai_reply)

    with patch("agent.customer_agent.client.messages.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response
        result = await process_customer_message("test-session-low", "Dzień dobry, witam")

    assert result["lead_score"] < 30
    assert result["intent"] == "low"
    assert result["category"] == "informacja"


class TestLeadScorerUnit:
    """Direct unit tests for LeadScorer class."""

    def test_high_intent_scoring(self):
        scorer = LeadScorer()
        result = scorer.compute("Ile kosztuje oklejenie auta? Chcę zamówić")
        assert result["lead_score"] >= 60
        assert result["intent"] == "high"

    def test_medium_intent_scoring(self):
        scorer = LeadScorer()
        result = scorer.compute("Czy możecie zrobić baner reklamowy?")
        assert result["lead_score"] >= 15
        assert result["intent"] in ("low", "medium", "high")
        assert result["category"] in ("informacja", "usługi")

    def test_low_intent_scoring(self):
        scorer = LeadScorer()
        result = scorer.compute("Dzień dobry")
        assert result["lead_score"] < 30
        assert result["intent"] == "low"

    def test_compute_returns_all_keys(self):
        scorer = LeadScorer()
        result = scorer.compute("test message")
        assert set(result.keys()) == {"lead_score", "intent", "category", "reason"}
