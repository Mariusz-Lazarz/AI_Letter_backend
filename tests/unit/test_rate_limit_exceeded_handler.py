import pytest
import json
from fastapi import Request
from slowapi.errors import RateLimitExceeded
from unittest.mock import patch, AsyncMock, MagicMock
from errors import rate_limit_exceeded_handler
from helpers.logger import AppLogger

@pytest.mark.asyncio
@pytest.mark.parametrize('exception, log_method, excpected_response', [(RateLimitExceeded(MagicMock(error_message="Rate limit exceeded")), 'log_warning', {"errors": ["Too many request please try again later!"]})])
async def test_rate_limit_exceeded_handler(exception, log_method, excpected_response):
    request = AsyncMock(spec=Request)

    with patch.object(AppLogger, log_method) as mock_log:
        response = await rate_limit_exceeded_handler(request, exception)
        
        assert response.status_code == 429
        assert json.loads(response.body) == excpected_response
        mock_log.assert_called_once_with(exception)