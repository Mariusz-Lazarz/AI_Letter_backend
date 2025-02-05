from db.db import Database
from fastapi import HTTPException, status
import logging

logging.basicConfig(level=logging.INFO, format=("%(asctime)s - %(levelname)s - - %(message)s"))
logger = logging.getLogger(__name__)

def get_db() -> Database:
    try:
        db = Database()
        return db
    except Exception as e:
        logger.exception(f"🚨 Database initialization failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is temporarily unavailable. Please try again later."
        )




