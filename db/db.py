import psycopg2.pool
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import logging
import config
import time
from fastapi import HTTPException, status

logging.basicConfig(level=logging.INFO, format=("%(asctime)s - %(levelname)s - - %(message)s"))
logger = logging.getLogger(__name__)



class Database:
    """ PostgreSQL Database connection class with connection pooling """

    _instance = None

    def __new__(cls): 
        if cls._instance is None: 
            cls._instance = super(Database, cls).__new__(cls) 
            cls._instance._init_pool() 
        return cls._instance 

    
    def _init_pool(self):
        try:
            self.pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1, maxconn=5, **config.DB_CONFIG
            )
            logger.info("✅ Database pool created successfully!")

        except psycopg2.OperationalError as e:
            logger.critical(f"❌ Database connection failed: {e}")
            raise
        except Exception as e:
            logger.exception("🚨 An unexpected error occurred while creating the pool.")
            raise

    def get_connection(self):
        """Get a connection from the pool with error handling."""
        MAX_RETRIES = 3
        RETRY_DELAY = 2
        
        for attempt in range(MAX_RETRIES):
            try:
                return self.pool.getconn()
            except Exception as e:
                logger.error(f"🚨 Failed to get a connection (Attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    raise
        
    def release_connection(self, conn):
        """Release a connection back to the pool safely."""
        try:
            if conn:
                self.pool.putconn(conn)
        except Exception as e:
            logger.error(f"⚠️ Failed to release connection: {e}")


    def close_pool(self):
        """Close all connections in the pool."""
        self.pool.closeall()
        logger.info("🔒 Database connection pool closed.")


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


if __name__ == "__main__":
    db = Database()
