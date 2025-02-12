import pytest
import json
from fastapi import Request
from unittest.mock import AsyncMock, patch
from errors import global_exception_handler
from helpers.logger import AppLogger

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception, log_method, expected_response",
    [
        (Exception(), "log_exception", {"errors": ["An error occurred. Try again later!"]}),
    ]
)
async def test_global_exception_handler(exception, log_method, expected_response):
    request = AsyncMock(spec=Request)
    
    with patch.object(AppLogger, log_method) as mock_log:
        response = await global_exception_handler(request, exception)
    
        assert response.status_code == 500
        assert json.loads(response.body.decode("utf-8")) == expected_response
        mock_log.assert_called_once_with(exception)
