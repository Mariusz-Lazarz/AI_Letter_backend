import jwt
import pytest
import datetime
from config import JWT_SECRET, JWT_ALGORITHM
from helpers.auth import verify_jwt 

def create_jwt(payload, secret=JWT_SECRET, algorithm=JWT_ALGORITHM, expire_seconds=3600):
    """Helper function to create a JWT token with a given payload and expiration time."""
    exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=expire_seconds)
    payload["exp"] = int(exp.timestamp())
    return jwt.encode(payload, secret, algorithm=algorithm)


def test_verify_jwt_valid_token():
    """Test that a valid JWT is decoded correctly."""
    payload = {"user_id": 1, "email": "test@example.com"}
    token = create_jwt(payload)
    
    decoded = verify_jwt(token)
    
    assert isinstance(decoded, dict)
    assert decoded["user_id"] == payload["user_id"]
    assert decoded["email"] == payload["email"]
    assert "exp" in decoded 

def test_verify_jwt_expired_token():
    """Test that an expired JWT raises an error."""
    payload = {"user_id": 1}
    expired_token = create_jwt(payload, expire_seconds=-10) 
    
    with pytest.raises(jwt.ExpiredSignatureError):
        verify_jwt(expired_token)

def test_verify_jwt_invalid_signature():
    """Test that a JWT with an invalid signature raises an error."""
    payload = {"user_id": 1}
    token = create_jwt(payload, secret="wrong_secret")
    
    with pytest.raises(jwt.InvalidSignatureError):
        verify_jwt(token)

def test_verify_jwt_malformed_token():
    """Test that a malformed JWT raises an error."""
    malformed_token = "this.is.not.a.jwt"
    
    with pytest.raises(jwt.DecodeError):
        verify_jwt(malformed_token)
