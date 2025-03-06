import pytest
from schemas.user import UserCreate

@pytest.mark.parametrize(
    "password, expected_exception, expected_message",
    [
        ("ValidPassword123!", None, None),  
        ("Valid", ValueError, "Password must be at least 8 characters long"),  
        ("ValidValidValidValidValidValidValid", ValueError, "Password cannot be longer than 32 characters long"),
        ("validpassword123!", ValueError, "Password must contain at least one uppercase letter"),  
        ("Validpassword!", ValueError, "Password must contain at least one number"),  
        ("Validpassword123", ValueError, "Password must contain at least one special character"),
    ]
)
def test_user_create_password_validation(password, expected_exception, expected_message):
    """Test password validation in UserCreate model."""
    if expected_exception:
        with pytest.raises(expected_exception, match=expected_message):
            UserCreate(email="valid.email@example.com", password=password, confirm_password=password)
    else:
        user = UserCreate(email="valid.email@example.com", password=password, confirm_password=password)
        assert user.password == password
