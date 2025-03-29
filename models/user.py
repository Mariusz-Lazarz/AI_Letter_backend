from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from typing import Optional, List
import uuid


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    role: str = Field(default="user")
    is_verified: bool = Field(default=False)
    verification_token: Optional[str] = Field(nullable=True)
    password_reset_token: Optional[str] = Field(nullable=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    cvs: List["UserCV"] = Relationship(back_populates="user")


class UserCV(SQLModel, table=True):
    __tablename__ = "user_cvs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)

    s3_key: str
    original_name: str

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: Optional[User] = Relationship(back_populates="cvs")
