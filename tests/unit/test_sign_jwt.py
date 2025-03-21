import jwt
import pytest
import datetime
from config import JWT_ALGORITHM, JWT_SECRET
from helpers.auth import sign_jwt


@pytest.mark.parametrize(
    "data",
    [
        ({"user_id": 1, "username": "testuser"}),
        ({"email": "test@example.com"}),
        ({"role": "admin", "permissions": ["read", "write"]}),
    ],
)
def test_sign_jwt(data):
    """Test JWT signing with different payloads."""
    token = sign_jwt(data)

    assert isinstance(token, str)

    decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

    for key in data:
        assert decoded[key] == data[key]

    assert "exp" in decoded
    expected_exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        seconds=3600
    )
    assert abs(decoded["exp"] - int(expected_exp.timestamp())) <= 5
