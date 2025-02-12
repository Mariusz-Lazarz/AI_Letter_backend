from pydantic import BaseModel, field_validator
import re

class UserCreate(BaseModel):
    email: str
    password: str

    @field_validator("email")
    def validate_email(cls, value):
        """Custom email validation to match frontend logic"""
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, value):
            raise ValueError("Invalid email format")
        return value

    @field_validator("password")
    def validate_password(cls, value):
        """Password validation (matches frontend rules)"""
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if len(value) > 32:
            raise ValueError("Password cannot be longer than 32 characters long")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character")
        return value
