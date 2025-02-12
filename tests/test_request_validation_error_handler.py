import pytest
import json
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from unittest.mock import AsyncMock, patch
from errors import request_validation_error_handler
from helpers.logger import AppLogger

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "errors, log_method, expected_response, expected_log_message",
    [
        (
            [{"loc": ["body", "email"], "msg": "Value error, Invalid email format"}],
            "log_warning",
            {"errors": [{"field": "body.email", "message": "Value error, Invalid email format"}]},
            "Validation error at http://127.0.0.1/test: " + json.dumps(
                [{"field": "body.email", "message": "Value error, Invalid email format"}], 
                ensure_ascii=False, indent=2
            )
        ),
        (
            [
                {"loc": ["body", "email"], "msg": "Value error, Invalid email format"},
                {"loc": ["body", "password"], "msg": "Value error, Invalid password format"}
            ],
            "log_warning",
            {"errors": [
                {"field": "body.email", "message": "Value error, Invalid email format"},
                {"field": "body.password", "message": "Value error, Invalid password format"}
            ]},
            "Validation error at http://127.0.0.1/test: " + json.dumps(
                [
                    {"field": "body.email", "message": "Value error, Invalid email format"},
                    {"field": "body.password", "message": "Value error, Invalid password format"}
                ], 
                ensure_ascii=False, indent=2
            )
        )
    ]
)
async def test_request_validation_error_handler(errors, log_method, expected_response, expected_log_message):
    request = AsyncMock(spec=Request)
    request.url = "http://127.0.0.1/test"
    exc = RequestValidationError(errors=errors)
    
    with patch.object(AppLogger, log_method) as mock_log:
        response = await request_validation_error_handler(request, exc)
    
        assert response.status_code == 422
        assert json.loads(response.body.decode("utf-8")) == expected_response
        mock_log.assert_called_once_with(expected_log_message)

@pytest.mark.asyncio
@patch.object(AppLogger, "log_error")
async def test_request_validation_error_handler_no_error(mock_log_error):
    request = AsyncMock(spec=Request)
    request.url = "http://127.0.0.1/test"
    exc = RequestValidationError(errors=[])
    
    with pytest.raises(Exception, match="RequestValidationError raised with an empty error list."):
        await request_validation_error_handler(request, exc)
    
    expected_log_message = f"RequestValidationError with empty errors list at {request.url}"
    mock_log_error.assert_called_once_with(expected_log_message)
