"""
Tests for Customer Chat Widget API.
"""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from api.app import create_app; app = create_app()
from agent.customer_agent import _customer_sessions_cache, SYSTEM_PROMPT

@pytest.fixture(autouse=True)
async def clear_cache():
    """Fixture to clear the customer session cache before each test."""
    _customer_sessions_cache.clear()
    yield
    _customer_sessions_cache.clear()

def test_customer_chat_endpoint_success():
    """
    Tests the /api/v1/widget/chat endpoint for a successful interaction.
    Mocks the process_customer_message function to return a valid response.
    """
    client = TestClient(app)
    
    with patch("agent.customer_agent.process_customer_message", new_callable=AsyncMock) as mock_process:
        mock_process.return_value = {
            "reply": "This is a test reply.",
            "lead": {"score": 10, "intent": "low", "category": "informacja", "reason": "test"}
        }

        response = client.post(
            "/api/v1/widget/chat",
            json={"session_id": "test-session-123", "message": "Hello, world!"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["reply"] == "This is a test reply."
        assert "lead" in data
        assert data["lead"]["score"] == 10
        mock_process.assert_called_once_with(session_id="test-session-123", user_input="Hello, world!")

async def test_customer_chat_caching():
    """
    Tests if the chat history is being cached correctly across multiple calls.
    """
    # We don't use the TestClient here because we need to interact with the cache directly
    # and call the real process_customer_message function (with a mocked client).
    
    from agent.customer_agent import process_customer_message

    with patch("agent.customer_agent.client.messages.create", new_callable=AsyncMock) as mock_create:
        # First call
        mock_create.return_value.content = [AsyncMock(text='{"reply": "First reply", "lead": {}}')]
        result1 = await process_customer_message("test-session-cache", "First message")

        # Check if the history was stored in the cache
        history1 = _customer_sessions_cache.get("test-session-cache")
        assert len(history1) == 2  # user message + assistant reply
        assert history1[0]["content"] == "First message"

        # Second call — fresh mock, still inside patch
        # Capture messages at call time (before process_customer_message mutates the list)
        captured_messages = []
        def capture_messages(*args, **kwargs):
            captured_messages.append(list(kwargs.get("messages", [])))
            return mock_create.return_value
        mock_create.side_effect = capture_messages
        mock_create.return_value.content = [AsyncMock(text='{"reply": "Second reply", "lead": {}}')]
        result2 = await process_customer_message("test-session-cache", "Second message")

        # Check history again, it should be longer
        history2 = _customer_sessions_cache.get("test-session-cache")
        assert len(history2) == 4
        assert history2[2]["content"] == "Second message"

        # Verify that the history from the first call was passed to the AI on the second call
        messages = captured_messages[0]
        assert len(messages) == 3
        assert messages[0]['role'] == 'user' and messages[0]['content'] == 'First message'
        assert messages[1]['role'] == 'assistant'
        assert messages[2]['role'] == 'user' and messages[2]['content'] == 'Second message'
