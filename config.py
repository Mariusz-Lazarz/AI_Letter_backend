from dotenv import load_dotenv
import os

load_dotenv()

URL_DATABASE = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
BASE_DOMAIN = os.getenv("BASE_DOMAIN") or "http://127.0.0.1:8000"
JWT_SECRET = os.getenv('JWT_SECRET')
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
BCRYPT_SALT = 8
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = os.getenv("SMTP_PORT")



# RATE LIMITS
RATE_LIMIT_REGISTER = "10/hour"