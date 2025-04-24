import pytest
import sys
import os
import uuid
from unittest.mock import MagicMock
from models.user import User, UserCV
from helpers.auth import hash_password, sign_jwt
from helpers.email_sender import EmailSender
from fastapi.testclient import TestClient
from sqlmodel import Session, delete
from database import create_db_and_tables, engine
from main import app
from config import RESET_PASSWORD_TOKEN

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Ensures the real database is set up before tests start."""
    print("🛠 Setting up REAL database for integration tests...")
    create_db_and_tables()


@pytest.fixture
def client():
    """Provides a FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def email_sender():
    """Provides a fully mocked EmailSender instance."""
    mock_sender = MagicMock(spec=EmailSender)

    mock_sender.account_confirmation.return_value = True

    return mock_sender


@pytest.fixture(scope="module")
def test_user():
    """Fixture to create a test user for login and CRUD tests, then remove it after."""
    unique_test_email = f"testuser+{uuid.uuid4().hex}@example.com"
    test_password = "TestPassword123!"
    verification_token = sign_jwt({"email": unique_test_email})
    hashed_password = hash_password(test_password)

    user = User(
        email=unique_test_email,
        password_hash=hashed_password,
        verification_token=verification_token,
    )

    try:
        with Session(engine) as session:
            session.add(user)
            session.commit()
            session.refresh(user)

        yield {
            "email": unique_test_email,
            "password": test_password,
            "verification_token": verification_token,
        }

    finally:
        with Session(engine) as session:
            session.exec(delete(User).where(User.email == unique_test_email))
            session.commit()


@pytest.fixture(scope="module")
def verified_test_user():
    """Fixture to create a verified test user with a CV for testing."""
    unique_test_email = f"verifieduser+{uuid.uuid4().hex}@example.com"
    test_password = "VerifiedTestPassword123!"
    password_reset_token = sign_jwt({"email": unique_test_email}, RESET_PASSWORD_TOKEN)
    hashed_password = hash_password(test_password)

    try:
        with Session(engine) as session:
            user = User(
                email=unique_test_email,
                password_hash=hashed_password,
                verification_token="",
                password_reset_token=password_reset_token,
                is_verified=True,
            )

            session.add(user)
            session.commit()
            session.refresh(user)

            user_cv = UserCV(
                id=uuid.uuid4(),
                user_id=user.id,
                s3_key="some_key",
                original_name="test_name",
            )
            session.add(user_cv)
            session.commit()

            user_data = {
                "id": user.id,
                "email": user.email,
                "password": test_password,
                "password_reset_token": password_reset_token,
                "user_cv_id": user_cv.id,
            }

        yield user_data

    finally:
        with Session(engine) as session:
            session.exec(delete(UserCV).where(UserCV.user_id == user_data["id"]))
            session.exec(delete(User).where(User.email == user_data["email"]))
            session.commit()
