from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException
from helpers.db import get_user_by_email


def test_get_user_by_email_success():
    mock_email = "test@example.com"

    mock_session = MagicMock()
    mock_session.exec.return_value.first.return_value = mock_email

    result = get_user_by_email(mock_session, "test@example.com")

    mock_session.exec.assert_called_once()
    assert result == mock_email


def test_get_user_by_email_not_found():
    mock_session = MagicMock()
    mock_session.exec.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        get_user_by_email(mock_session, "notfound@example.com")

    mock_session.exec.assert_called_once()
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"
