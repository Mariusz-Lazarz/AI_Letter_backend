import pytest
import sys
import os
import pytest
import uuid
from database import engine
from unittest.mock import MagicMock
from models.user import User
from helpers.auth import hash_password, sign_jwt
from helpers.email_sender import EmailSender
from fastapi.testclient import TestClient
from sqlmodel import Session, select, delete
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from database import engine, get_session, create_db_and_tables
from main import app

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

@pytest.fixture
def override_db():
    """Override database session for integration tests (without wiping data)."""
    def _override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = _override_get_session
    yield
    app.dependency_overrides.clear() 

@pytest.fixture(scope="module")
def test_user():
    """Fixture to create a test user for login and CRUD tests, then remove it after."""
    unique_test_email = f"testuser+{uuid.uuid4().hex}@example.com"
    test_password = "TestPassword123!" 
    verification_token = sign_jwt({"email": unique_test_email})
    hashed_password = hash_password(test_password) 
    

    user = User(email=unique_test_email, password_hash=hashed_password, verification_token=verification_token)

    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)

    yield {"email": unique_test_email, "password": test_password}

    with Session(engine) as session:
        session.exec(delete(User).where(User.email == unique_test_email))
        session.commit()