import logging
import sys

class AppLogger:
    """Centralized logging utility for FastAPI application."""

    def __init__(self, log_file: str = "app.log", logger_name: str = "fastapi_app"):
        """Initialize logger with both console and file handlers."""
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)

        if not self.logger.hasHandlers():
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            console_handler.setFormatter(console_format)
            self.logger.addHandler(console_handler)

            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            file_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)

    def log_info(self, message: str):
        """Log an INFO message."""
        self.logger.info(message)

    def log_warning(self, message: str):
        """Log a WARNING message."""
        self.logger.warning(message)

    def log_error(self, message: str):
        """Log an ERROR message."""
        self.logger.error(message)

    def log_exception(self, exception: Exception):
        """Log an exception with traceback."""
        self.logger.exception(f"Exception occurred: {exception}")
