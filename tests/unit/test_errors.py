import pytest
import json
from fastapi import Request
from unittest.mock import AsyncMock, patch
from errors import jwt_invalid_signature_handler, jwt_expired_signature_handler, jwt_malformed_token_handler
from helpers.logger import AppLogger
from jwt import InvalidSignatureError, DecodeError, ExpiredSignatureError

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception, log_method, expected_response, error_handler, message_prefix",
    [
        (InvalidSignatureError(), "log_warning", {"errors": ["Unauthorized"]}, jwt_invalid_signature_handler, "Invalid JWT Signature at:"),
        (ExpiredSignatureError(), "log_warning", {"errors": ["Unauthorized"]}, jwt_expired_signature_handler, "Expired JWT Signature at:"),
         (DecodeError(), "log_warning", {"errors": ["Unauthorized"]}, jwt_malformed_token_handler, "Malformed Token at:")    
    ]
)
async def test_jwt_handler(exception, log_method, expected_response, error_handler, message_prefix):
    request = AsyncMock(spec=Request)
    
    with patch.object(AppLogger, log_method) as mock_log:
        response = await error_handler(request, exception)
    
        assert response.status_code == 401
        assert json.loads(response.body.decode("utf-8")) == expected_response
        mock_log.assert_called_once_with(f"{message_prefix} {request.url}, token: {request.cookies.get('refresh_token')}")

