import pytest
import uuid
from fastapi.testclient import TestClient
from unittest.mock import patch
from sqlmodel import Session, select, delete
from database import engine
from models.user import User

def test_register_user(client):
    """Test the user registration API using a real database (with cleanup)."""
    
    unique_test_email = f"testuser+{uuid.uuid4().hex}@example.com"

    test_user = {
        "email": unique_test_email,
        "password": "TestPassword123!"
    }

    try:
        response = client.post("/auth/register", json=test_user)
        
        assert response.status_code == 201
        assert response.json() == {"data": {"message": "User created successfully"}}

        with Session(engine) as session:
            result = session.exec(select(User).where(User.email == test_user["email"])).first()
            assert result is not None 
            assert result.email == test_user["email"] 

    finally:
        with Session(engine) as session:
            session.exec(delete(User).where(User.email == unique_test_email))
            session.commit()
            print(f"🗑️ Deleted test user: {unique_test_email}")


def test_register_existing_user(client, test_user):
    """Test that registering an already existing user fails with 400 error."""
    
    test_user_data = {
        "email": test_user["email"],
        "password": "NewTestPassword!"
    }

    response = client.post("/auth/register", json=test_user_data)

    assert response.status_code == 422

def test_register_email_sent(client, email_sender):
    """Test that the account confirmation email is sent upon registration."""

    unique_test_email = f"testuser+{uuid.uuid4().hex}@example.com"

    test_user = {
        "email": unique_test_email,
        "password": "TestPassword123!"
    }

    with patch("routers.auth.email_sender", email_sender):
        response = client.post("/auth/register", json=test_user)

    assert response.status_code == 201

    email_sender.account_confirmation.assert_called_once()

    args, kwargs = email_sender.account_confirmation.call_args
    print("📌 Captured Args:", args)
    print("📌 Captured Kwargs:", kwargs)

    sent_email = kwargs.get("to_email")
    sent_token = kwargs.get("verification_token")

    assert sent_email == unique_test_email  
    assert sent_token is not None 
    assert isinstance(sent_token, str)

    with Session(engine) as session:
            session.exec(delete(User).where(User.email == unique_test_email))
            session.commit()
            print(f"🗑️ Deleted test user: {unique_test_email}")


def test_user_persisted_after_registration(client):
    """Ensure user is saved in the database after successful registration."""
    
    unique_test_email = f"testuser+{uuid.uuid4().hex}@example.com"

    test_user = {
        "email": unique_test_email,
        "password": "TestPassword123!"
    }

    client.post("/auth/register", json=test_user)

    with Session(engine) as session:
        result = session.exec(select(User).where(User.email == test_user["email"])).first()
        assert result is not None  
        assert result.email == test_user["email"]

    with Session(engine) as session:
            session.exec(delete(User).where(User.email == unique_test_email))
            session.commit()
            print(f"🗑️ Deleted test user: {unique_test_email}")
