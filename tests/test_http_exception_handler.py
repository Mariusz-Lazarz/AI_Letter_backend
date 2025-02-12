import pytest
import json
from fastapi import Request, HTTPException
from unittest.mock import AsyncMock, patch
from errors import http_exception_handler
from helpers.logger import AppLogger

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status_code, detail, log_method",
    [
        (500, "Internal Server Error", "log_error"),
        (400, "Invalid request data", "log_warning"),
        (404, "Not Found", "log_warning"),
    ]
)
async def test_http_exception_handler(status_code, detail, log_method):
    request = AsyncMock(spec=Request)
    request.url = "http://127.0.0.1/test"
    exc = HTTPException(status_code=status_code, detail=detail)
    
    expected_message = f"HTTP Exception at {request.url}: {exc.detail}"
    expected_response = {"errors": [detail]}
    
    with patch.object(AppLogger, log_method) as mock_log:
        response = await http_exception_handler(request, exc)
    
        assert response.status_code == status_code
        assert json.loads(response.body.decode("utf-8")) == expected_response
        mock_log.assert_called_once_with(expected_message)
