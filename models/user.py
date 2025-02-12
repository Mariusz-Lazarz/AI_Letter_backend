from sqlmodel import Field, SQLModel
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String

from typing import Optional

class User(SQLModel, table=True):
    __tablename__ = 'users'

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(sa_column=Column(String, unique=True))
    password_hash: str
    role: str = Field(default="user")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

