import pytest
import json
from fastapi import Request
from sqlalchemy.exc import IntegrityError
from unittest.mock import AsyncMock, patch
from errors import integrity_error_handler
from helpers.logger import AppLogger

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error_message, expected_response, log_method, log_message",
    [
        (
            'Key (email)=(test@example.com) already exists',
            {"errors": [{"field": "email", "message": "test@example.com is already taken"}]},
            "log_warning",
            "IntegrityError at http://127.0.0.1/test: Duplicate field(s) ['email'] with value(s) ['test@example.com']"
        ),
        (
            'Some random database error occurred',
            {"errors": [{"message": "Database integrity error"}]},
            "log_error",
            "IntegrityError at http://127.0.0.1/test: Some random database error occurred"
        ),
        (
            None,
            {"errors": [{"message": "Database integrity error"}]},
            "log_error",
            "IntegrityError at http://127.0.0.1/test: None"
        ),
        (
            'Key (username, email)=(testuser, test@example.com) already exists',
            {"errors": [
                {"field": "username", "message": "testuser is already taken"},
                {"field": "email", "message": "test@example.com is already taken"}
            ]},
            "log_warning",
            "IntegrityError at http://127.0.0.1/test: Duplicate field(s) ['username', 'email'] with value(s) ['testuser', 'test@example.com']"
        )
    ]
)
async def test_integrity_error_handler(error_message, expected_response, log_method, log_message):
    class FakeOrig:
        def __str__(self):
            return error_message if error_message is not None else ''

    request = AsyncMock(spec=Request)
    request.url = "http://127.0.0.1/test"
    exc = IntegrityError(statement=None, params=None, orig=FakeOrig() if error_message is not None else None)
    
    with patch.object(AppLogger, log_method) as mock_log:
        response = await integrity_error_handler(request, exc)
    
        assert response.status_code == 409
        assert json.loads(response.body.decode("utf-8")) == expected_response
        mock_log.assert_called_once_with(log_message)
