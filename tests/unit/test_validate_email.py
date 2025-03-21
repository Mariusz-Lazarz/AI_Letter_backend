# import pytest
# from schemas.user import UserCreate

# @pytest.mark.parametrize(
#     "email, expected_exception, expected_message",
#     [
#         ("valid.email@example.com", None, None),
#         ("invalid-email.com", ValueError, "Invalid email format"),
#         ("@example.com", ValueError, "Invalid email format"),
#         ("user@@example.com", ValueError, "Invalid email format"),
#         ("user@example", ValueError, "Invalid email format"),
#         ("user@.com", ValueError, "Invalid email format"),
#     ]
# )
# def test_user_create_email_validation(email, expected_exception, expected_message):
#     """Test email validation in UserCreate model."""
#     if expected_exception:
#         with pytest.raises(expected_exception, match=expected_message):
#             UserCreate(email=email, password="Valid123!")
#     else:
#         user = UserCreate(email=email, password="Valid123!")
#         assert user.email == email
