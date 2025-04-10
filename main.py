from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import IntegrityError
from fastapi.exceptions import RequestValidationError
from routers import auth, cv, letter
from slowapi.errors import RateLimitExceeded
from jwt import InvalidSignatureError, ExpiredSignatureError, DecodeError
import errors

app = FastAPI()

app.include_router(auth.router)
app.include_router(cv.router)
app.include_router(letter.router)

app.add_exception_handler(RateLimitExceeded, errors.rate_limit_exceeded_handler)
app.add_exception_handler(IntegrityError, errors.integrity_error_handler)
app.add_exception_handler(
    RequestValidationError, errors.request_validation_error_handler
)
app.add_exception_handler(InvalidSignatureError, errors.jwt_invalid_signature_handler)
app.add_exception_handler(ExpiredSignatureError, errors.jwt_expired_signature_handler)
app.add_exception_handler(DecodeError, errors.jwt_malformed_token_handler)
app.add_exception_handler(HTTPException, errors.http_exception_handler)
app.add_exception_handler(Exception, errors.global_exception_handler)
