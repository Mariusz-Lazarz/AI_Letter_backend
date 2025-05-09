import re
from fastapi import Request, HTTPException
from slowapi.errors import RateLimitExceeded
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from helpers.logger import AppLogger
import json
from jwt import InvalidSignatureError, ExpiredSignatureError, DecodeError

logger = AppLogger(log_file="app.log", logger_name="fastapi_app")


def build_response(errors, status_code):
    return JSONResponse(status_code=status_code, content={"errors": errors})


async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handles database integrity errors (unique constraint violations)."""
    match = re.search(r"Key \((.*?)\)=\((.*?)\) already exists", str(exc.orig))
    errors = []

    if match:
        fields = match.group(1).split(", ")
        values = match.group(2).split(", ")

        errors = [
            {"field": field, "message": f"{value} is already taken"}
            for field, value in zip(fields, values)
        ]
        logger.log_warning(
            f"IntegrityError at {request.url}: Duplicate field(s) {fields} with value(s) {values}"
        )
    else:
        errors = [{"message": "Database integrity error"}]
        logger.log_error(f"IntegrityError at {request.url}: {str(exc.orig)}")

    return build_response(errors=errors, status_code=409)


async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
):
    """Handles FastAPI request validation errors."""
    errors = [
        {"field": ".".join(map(str, err["loc"])), "message": err["msg"]}
        for err in exc.errors()
    ]

    if not errors:
        logger.log_error(
            f"RequestValidationError with empty errors list at {request.url}"
        )
        raise Exception("RequestValidationError raised with an empty error list.")

    logger.log_warning(
        f"Validation error at {request.url}: {json.dumps(errors, ensure_ascii=False, indent=2)}"
    )
    return build_response(errors=errors, status_code=422)


async def global_exception_handler(request: Request, exc: Exception):
    """Handles unexpected global exceptions."""
    logger.log_exception(exc)
    return build_response(
        errors=["An error occurred. Try again later!"], status_code=500
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handles FastAPI HTTP exceptions and logs them."""

    if exc.status_code >= 500:
        logger.log_error(f"HTTP Exception at {request.url}: {exc.detail}")
    else:
        logger.log_warning(f"HTTP Exception at {request.url}: {exc.detail}")
    return build_response(errors=exc.detail, status_code=exc.status_code)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    logger.log_warning(exc)
    return build_response(
        errors=["Too many request please try again later!"], status_code=429
    )


async def jwt_invalid_signature_handler(request: Request, exc: InvalidSignatureError):
    logger.log_warning(
        f"Invalid JWT Signature at: {request.url}, token: {request.cookies.get('refresh_token')}"
    )
    return build_response(errors=["Unauthorized"], status_code=401)


async def jwt_expired_signature_handler(request: Request, exc: ExpiredSignatureError):
    logger.log_warning(
        f"Expired JWT Signature at: {request.url}, token: {request.cookies.get('refresh_token')}"
    )
    return build_response(errors=["Unauthorized"], status_code=401)


async def jwt_malformed_token_handler(request: Request, exc: DecodeError):
    logger.log_warning(
        f"Malformed Token at: {request.url}, token: {request.cookies.get('refresh_token')}"
    )
    return build_response(errors=["Unauthorized"], status_code=401)
