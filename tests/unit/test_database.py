import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database import get_session
from unittest.mock import patch, MagicMock


@patch("database.Session")
def test_get_session(mock_session):
    mock_db = MagicMock()
    mock_session.return_value.__enter__.return_value = mock_db

    session = next(get_session())

    assert session is not None
    mock_session.assert_called_once()
    mock_session.return_value.__exit__.assert_called_once()

