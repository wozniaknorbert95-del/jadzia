"""Tests for retry mechanism."""

import pytest
import time
from agent.tools.ssh_pure import with_retry, async_with_retry


@pytest.mark.asyncio
async def test_retry_succeeds_on_second_attempt():
    """Retry should succeed if function works on retry."""
    call_count = [0]

    @async_with_retry(max_attempts=3, delay=0.1)
    async def flaky_function():
        call_count[0] += 1
        if call_count[0] < 2:
            raise Exception("Transient error")
        return "success"

    result = await flaky_function()
    assert result == "success"
    assert call_count[0] == 2


@pytest.mark.asyncio
async def test_retry_fails_after_max_attempts():
    """Retry should raise after max attempts."""
    call_count = [0]

    @async_with_retry(max_attempts=3, delay=0.1)
    async def always_fails():
        call_count[0] += 1
        raise Exception("Permanent error")

    with pytest.raises(Exception, match="Permanent error"):
        await always_fails()

    assert call_count[0] == 3


@pytest.mark.asyncio
async def test_retry_with_backoff():
    """Retry should use exponential backoff."""
    call_times = []

    @async_with_retry(max_attempts=3, delay=0.1, backoff=2.0)
    async def track_timing():
        call_times.append(time.time())
        raise Exception("Test")

    try:
        await track_timing()
    except Exception:
        pass

    assert len(call_times) == 3

    delay1 = call_times[1] - call_times[0]
    delay2 = call_times[2] - call_times[1]

    assert 0.08 < delay1 < 0.15
    assert 0.18 < delay2 < 0.25
