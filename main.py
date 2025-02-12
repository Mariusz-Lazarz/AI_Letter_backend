from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import IntegrityError
from fastapi.exceptions import RequestValidationError
import errors


app = FastAPI()

app.add_exception_handler(IntegrityError, errors.integrity_error_handler)
app.add_exception_handler(RequestValidationError, errors.request_validation_error_handler)
app.add_exception_handler(HTTPException, errors.http_exception_handler)
app.add_exception_handler(Exception, errors.global_exception_handler)



