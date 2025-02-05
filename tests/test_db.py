from db.db import Database, get_db
from unittest.mock import patch, MagicMock
import pytest
import psycopg2
import config
from fastapi import HTTPException, status

@pytest.fixture(autouse=True)
def reset_database_instance():
    """Automatically reset the Database singleton before every test."""
    Database._instance = None

@patch("psycopg2.pool.SimpleConnectionPool")
def test_init_pool(mock_pool):
    db = Database()
    assert db.pool is not None
    mock_pool.assert_called_once()

@patch("psycopg2.pool.SimpleConnectionPool", side_effect=Exception("DB Pool Error"))
def test_init_pool_failure(mock_pool, caplog: pytest.LogCaptureFixture):

    with caplog.at_level("ERROR"), pytest.raises(Exception, match="DB Pool Error"):
        db = Database()

    assert "🚨 An unexpected error occurred while creating the pool." in caplog.text

    mock_pool.assert_called_once()

@patch.dict(config.DB_CONFIG, {"password": "wrong_pass"}, clear=True)
def test_init_pool_incorrect_credential(caplog: pytest.LogCaptureFixture):

    with caplog.at_level("CRITICAL"), pytest.raises(psycopg2.OperationalError):
        db = Database()

    assert "❌ Database connection failed" in caplog.text

def test_init_pool_singelton():
    db1 = Database()
    db2 = Database()
    assert db1.pool is db2.pool

@patch("psycopg2.pool.SimpleConnectionPool")
def test_init_pool_not_reinitialized(mock_pool): 
    db1 = Database()
    db2 = Database()

    
    assert db1.pool is db2.pool


    mock_pool.assert_called_once()

def test_get_connection():
    db = Database()

    conn = db.get_connection() 
    assert conn is not None

@patch("psycopg2.pool.SimpleConnectionPool.getconn", side_effect=Exception("DB Conn Error"))
def test_get_connection_failure(mock_getconn, caplog: pytest.LogCaptureFixture): 

    db = Database()  

    with caplog.at_level("ERROR"), pytest.raises(Exception, match="DB Conn Error"):
        conn = db.get_connection()

    assert mock_getconn.call_count == 3

    assert "🚨 Failed to get a connection (Attempt 1/3): DB Conn Error" in caplog.text
    assert "🚨 Failed to get a connection (Attempt 2/3): DB Conn Error" in caplog.text
    assert "🚨 Failed to get a connection (Attempt 3/3): DB Conn Error" in caplog.text

@patch("time.sleep")
@patch("psycopg2.pool.SimpleConnectionPool.getconn", side_effect=Exception("DB Conn Error"))
def test_get_connection_failure_with_sleep(mock_getconn, mock_sleep, caplog: pytest.LogCaptureFixture):
    db = Database()

    MAX_RETRIES = 3
    RETRY_DELAY = 2

    with caplog.at_level("ERROR"), pytest.raises(Exception, match="DB Conn Error"):
        db.get_connection() 

    assert mock_sleep.call_count == MAX_RETRIES - 1 

    mock_sleep.assert_called_with(RETRY_DELAY)

    assert "🚨 Failed to get a connection (Attempt 1/3): DB Conn Error" in caplog.text
    assert "🚨 Failed to get a connection (Attempt 2/3): DB Conn Error" in caplog.text
    assert "🚨 Failed to get a connection (Attempt 3/3): DB Conn Error" in caplog.text


@patch("psycopg2.pool.SimpleConnectionPool.putconn")
def test_release_connection(mock_putconn):

    db = Database()

    conn = db.get_connection()

    assert conn is not None

    db.release_connection(conn)

    mock_putconn.assert_called_once_with(conn)

@patch("psycopg2.pool.SimpleConnectionPool.putconn")
def test_release_connection_with_none(mock_putconn):
    db = Database()
    db.release_connection(None)
    mock_putconn.assert_not_called()


@patch("psycopg2.pool.SimpleConnectionPool.putconn", side_effect=Exception("DB PutConn Error"))
def test_release_connection_failure(mock_putconn, caplog: pytest.LogCaptureFixture):  

    db = Database()

    conn = db.get_connection()

    assert conn is not None

    with caplog.at_level("ERROR"):
        db.release_connection(conn) 

    mock_putconn.assert_called_once_with(conn)
    assert "⚠️ Failed to release connection: DB PutConn Error" in caplog.text


@patch("psycopg2.pool.SimpleConnectionPool.closeall")
def test_close_pool(mock_closeall, caplog: pytest.LogCaptureFixture):

    db = Database()

    with caplog.at_level("INFO"):
        db.close_pool()

    mock_closeall.assert_called_once()

    assert "🔒 Database connection pool closed." in caplog.text

def test_get_db():
    db_instance = get_db()
    assert isinstance(db_instance, Database)


@patch("db.db.Database", side_effect=Exception("DB Initialization Error"))
def test_get_db_failure(mock_db, caplog):
    with caplog.at_level("ERROR"):
        with pytest.raises(HTTPException) as exc_info:
            get_db()

    assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert exc_info.value.detail == "Database is temporarily unavailable. Please try again later."

    assert "🚨 Database initialization failed: DB Initialization Error" in caplog.text