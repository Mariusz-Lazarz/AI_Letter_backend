from sqlmodel import Field, SQLModel
from datetime import datetime, timezone
from typing import Optional

class User(SQLModel, table=True):
    __tablename__ = 'users'

    id: int = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    role: str = Field(default="user")
    is_verified: bool = Field(default=False)
    verification_token: Optional[str] = Field(nullable=True)
    password_reset_token: Optional[str] = Field(nullable=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

