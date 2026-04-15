import pytest
from unittest.mock import AsyncMock
from app.core.retry import retry_async_call


@pytest.mark.asyncio
async def test_retry_succeeds_on_second_attempt():
    """Test that retry_async_call retries and succeeds."""
    call_count = 0
    
    async def flaky_operation():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ConnectionError("First attempt fails")
        return "success"
    
    result = await retry_async_call(
        flaky_operation,
        retries=3,
        exceptions=(ConnectionError,)
    )
    
    assert result == "success"
    assert call_count == 2  


@pytest.mark.asyncio
async def test_retry_exhausts_attempts():
    """Test that retry_async_call raises after exhausting retries."""
    async def always_fails():
        raise ConnectionError("Always fails")
    
    with pytest.raises(ConnectionError, match="Always fails"):
        await retry_async_call(
            always_fails,
            retries=3,
            exceptions=(ConnectionError,)
        )


@pytest.mark.asyncio
async def test_retry_only_retries_specified_exceptions():
    """Test that only specified exceptions are retried."""
    async def fails_with_different_error():
        raise ValueError("Not in exceptions list")
    
    with pytest.raises(ValueError, match="Not in exceptions list"):
        await retry_async_call(
            fails_with_different_error,
            retries=3,
            exceptions=(ConnectionError, TimeoutError)
        )