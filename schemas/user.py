from pydantic import BaseModel, EmailStr, field_validator
import re

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

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

class UserLogin(UserCreate):
    pass


