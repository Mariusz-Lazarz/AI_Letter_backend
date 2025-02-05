from fastapi import HTTPException, status
from main import get_db
import pytest
from unittest.mock import patch
from db.db import Database

def test_get_db():
    db_instance = get_db()
    assert isinstance(db_instance, Database)


@patch("main.Database", side_effect=Exception("DB Initialization Error"))
def test_get_db_failure(mock_db, caplog):
    with caplog.at_level("ERROR"):
        with pytest.raises(HTTPException) as exc_info:
            get_db()

    assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert exc_info.value.detail == "Database is temporarily unavailable. Please try again later."

    assert "🚨 Database initialization failed: DB Initialization Error" in caplog.text





    
