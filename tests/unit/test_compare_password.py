import pytest
import bcrypt
from helpers.auth import compare_password, hash_password

@pytest.mark.parametrize(
    "password, should_match",
    [
        ("correct_password", True),
        ("wrong_password", False),
    ]
)
def test_compare_password(password, should_match):
    correct_password = "correct_password"
    hashed_password = hash_password(correct_password)

    result = compare_password(password, hashed_password)

    assert result is should_match
