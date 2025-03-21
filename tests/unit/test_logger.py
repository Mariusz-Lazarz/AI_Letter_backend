import pytest
import logging
from helpers.logger import AppLogger


@pytest.fixture
def app_logger():
    return AppLogger()


@pytest.mark.parametrize(
    "log_method, message, expected_level",
    [
        ("log_info", "This is an info message", logging.INFO),
        ("log_warning", "This is a warning message", logging.WARNING),
        ("log_error", "This is an error message", logging.ERROR),
    ],
)
def test_app_logger_methods(app_logger, log_method, message, expected_level, caplog):
    with caplog.at_level(expected_level):
        getattr(app_logger, log_method)(message)

    assert message in caplog.text


@pytest.mark.parametrize(
    "exception, expected_log_message",
    [
        (
            ValueError("Value error occurred"),
            "Exception occurred: Value error occurred",
        ),
        (
            RuntimeError("Runtime error occurred"),
            "Exception occurred: Runtime error occurred",
        ),
    ],
)
def test_app_logger_exception(app_logger, exception, expected_log_message, caplog):
    with caplog.at_level(logging.ERROR):
        app_logger.log_exception(exception)

    assert expected_log_message in caplog.text
