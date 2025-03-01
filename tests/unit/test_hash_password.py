import pytest
from helpers.auth import hash_password
import bcrypt

@pytest.mark.parametrize(
    "password, expected_type",
    [
        ("password123", str),
    ]
)
def test_hash_password(password, expected_type):
    password_hash = hash_password(password)
    
    assert isinstance(password_hash, expected_type)
    assert bcrypt.checkpw(password.encode(), password_hash.encode())

def test_hash_is_unique():
    """Test that the same password does not always produce the same hash (due to salting)."""
    password = "securepassword"
    hash1 = hash_password(password)
    hash2 = hash_password(password)

    assert hash1 != hash2  
    assert bcrypt.checkpw(password.encode(), hash1.encode())
    assert bcrypt.checkpw(password.encode(), hash2.encode())
