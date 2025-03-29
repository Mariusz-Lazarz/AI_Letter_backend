from sqlalchemy.exc import IntegrityError
import pytest
import json
from fastapi import HTTPException, Request
from unittest.mock import AsyncMock, patch, MagicMock
from errors import (
    global_exception_handler,
    http_exception_handler,
    integrity_error_handler,
    jwt_invalid_signature_handler,
    jwt_expired_signature_handler,
    jwt_malformed_token_handler,
    rate_limit_exceeded_handler,
    request_validation_error_handler,
)
from helpers.logger import AppLogger
from jwt import InvalidSignatureError, DecodeError, ExpiredSignatureError
from fastapi.exceptions import RequestValidationError
from slowapi.errors import RateLimitExceeded


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception, log_method, expected_response, error_handler, message_prefix",
    [
        (
            InvalidSignatureError(),
            "log_warning",
            {"errors": ["Unauthorized"]},
            jwt_invalid_signature_handler,
            "Invalid JWT Signature at:",
        ),
        (
            ExpiredSignatureError(),
            "log_warning",
            {"errors": ["Unauthorized"]},
            jwt_expired_signature_handler,
            "Expired JWT Signature at:",
        ),
        (
            DecodeError(),
            "log_warning",
            {"errors": ["Unauthorized"]},
            jwt_malformed_token_handler,
            "Malformed Token at:",
        ),
    ],
)
async def test_jwt_handler(
    exception, log_method, expected_response, error_handler, message_prefix
):
    request = AsyncMock(spec=Request)

    with patch.object(AppLogger, log_method) as mock_log:
        response = await error_handler(request, exception)

        assert response.status_code == 401
        assert json.loads(response.body.decode("utf-8")) == expected_response
        mock_log.assert_called_once_with(
            f"{message_prefix} {request.url}, token: {request.cookies.get('refresh_token')}"
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "errors, log_method, expected_response, expected_log_message",
    [
        (
            [
                {
                    "loc": ["body", "email"],
                    "msg": "Value error, Invalid email format",
                }
            ],
            "log_warning",
            {
                "errors": [
                    {
                        "field": "body.email",
                        "message": "Value error, Invalid email format",
                    }
                ]
            },
            "Validation error at http://127.0.0.1/test: "
            + json.dumps(
                [
                    {
                        "field": "body.email",
                        "message": "Value error, Invalid email format",
                    }
                ],
                ensure_ascii=False,
                indent=2,
            ),
        ),
        (
            [
                {
                    "loc": ["body", "email"],
                    "msg": "Value error, Invalid email format",
                },
                {
                    "loc": ["body", "password"],
                    "msg": "Value error, Invalid password format",
                },
            ],
            "log_warning",
            {
                "errors": [
                    {
                        "field": "body.email",
                        "message": "Value error, Invalid email format",
                    },
                    {
                        "field": "body.password",
                        "message": "Value error, Invalid password format",
                    },
                ]
            },
            "Validation error at http://127.0.0.1/test: "
            + json.dumps(
                [
                    {
                        "field": "body.email",
                        "message": "Value error, Invalid email format",
                    },
                    {
                        "field": "body.password",
                        "message": "Value error, Invalid password format",
                    },
                ],
                ensure_ascii=False,
                indent=2,
            ),
        ),
    ],
)
async def test_request_validation_error_handler(
    errors, log_method, expected_response, expected_log_message
):
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

    with pytest.raises(
        Exception,
        match="RequestValidationError raised with an empty error list.",
    ):
        await request_validation_error_handler(request, exc)

    expected_log_message = (
        f"RequestValidationError with empty errors list at {request.url}"
    )
    mock_log_error.assert_called_once_with(expected_log_message)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception, log_method, expected_response",
    [
        (
            Exception(),
            "log_exception",
            {"errors": ["An error occurred. Try again later!"]},
        ),
    ],
)
async def test_global_exception_handler(exception, log_method, expected_response):
    request = AsyncMock(spec=Request)

    with patch.object(AppLogger, log_method) as mock_log:
        response = await global_exception_handler(request, exception)

        assert response.status_code == 500
        assert json.loads(response.body.decode("utf-8")) == expected_response
        mock_log.assert_called_once_with(exception)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status_code, detail, log_method",
    [
        (500, "Internal Server Error", "log_error"),
        (400, "Invalid request data", "log_warning"),
        (404, "Not Found", "log_warning"),
    ],
)
async def test_http_exception_handler(status_code, detail, log_method):
    request = AsyncMock(spec=Request)
    request.url = "http://127.0.0.1/test"
    exc = HTTPException(status_code=status_code, detail=detail)

    expected_message = f"HTTP Exception at {request.url}: {exc.detail}"
    expected_response = {"errors": detail}

    with patch.object(AppLogger, log_method) as mock_log:
        response = await http_exception_handler(request, exc)

        assert response.status_code == status_code
        assert json.loads(response.body.decode("utf-8")) == expected_response
        mock_log.assert_called_once_with(expected_message)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error_message, expected_response, log_method, log_message",
    [
        (
            "Key (email)=(test@example.com) already exists",
            {
                "errors": [
                    {
                        "field": "email",
                        "message": "test@example.com is already taken",
                    }
                ]
            },
            "log_warning",
            "IntegrityError at http://127.0.0.1/test: Duplicate field(s) ['email'] with value(s) ['test@example.com']",
        ),
        (
            "Some random database error occurred",
            {"errors": [{"message": "Database integrity error"}]},
            "log_error",
            "IntegrityError at http://127.0.0.1/test: Some random database error occurred",
        ),
        (
            None,
            {"errors": [{"message": "Database integrity error"}]},
            "log_error",
            "IntegrityError at http://127.0.0.1/test: None",
        ),
        (
            "Key (username, email)=(testuser, test@example.com) already exists",
            {
                "errors": [
                    {
                        "field": "username",
                        "message": "testuser is already taken",
                    },
                    {
                        "field": "email",
                        "message": "test@example.com is already taken",
                    },
                ]
            },
            "log_warning",
            "IntegrityError at http://127.0.0.1/test: Duplicate field(s) ['username', 'email'] with value(s) ['testuser', 'test@example.com']",
        ),
    ],
)
async def test_integrity_error_handler(
    error_message, expected_response, log_method, log_message
):
    class FakeOrig:
        def __str__(self):
            return error_message if error_message is not None else ""

    request = AsyncMock(spec=Request)
    request.url = "http://127.0.0.1/test"
    exc = IntegrityError(
        statement=None,
        params=None,
        orig=FakeOrig() if error_message is not None else None,
    )

    with patch.object(AppLogger, log_method) as mock_log:
        response = await integrity_error_handler(request, exc)

        assert response.status_code == 409
        assert json.loads(response.body.decode("utf-8")) == expected_response
        mock_log.assert_called_once_with(log_message)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception, log_method, excpected_response",
    [
        (
            RateLimitExceeded(MagicMock(error_message="Rate limit exceeded")),
            "log_warning",
            {"errors": ["Too many request please try again later!"]},
        )
    ],
)
async def test_rate_limit_exceeded_handler(exception, log_method, excpected_response):
    request = AsyncMock(spec=Request)

    with patch.object(AppLogger, log_method) as mock_log:
        response = await rate_limit_exceeded_handler(request, exception)

        assert response.status_code == 429
        assert json.loads(response.body) == excpected_response
        mock_log.assert_called_once_with(exception)
