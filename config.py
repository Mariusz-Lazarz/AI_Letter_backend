from dotenv import load_dotenv
import os

load_dotenv()

URL_DATABASE = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

BCRYPT_SALT = 8