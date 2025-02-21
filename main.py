from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import IntegrityError
from fastapi.exceptions import RequestValidationError
from routers import auth
from slowapi.errors import RateLimitExceeded
import errors

app = FastAPI()

app.include_router(auth.router)

app.add_exception_handler(RateLimitExceeded, errors.rate_limit_exceeded_handler)
app.add_exception_handler(IntegrityError, errors.integrity_error_handler)
app.add_exception_handler(RequestValidationError, errors.request_validation_error_handler)
app.add_exception_handler(HTTPException, errors.http_exception_handler)
app.add_exception_handler(Exception, errors.global_exception_handler)
