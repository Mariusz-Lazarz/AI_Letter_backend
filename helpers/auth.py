import bcrypt
import datetime
import jwt
from config import BCRYPT_SALT, JWT_SECRET, JWT_ALGORITHM

def hash_password(password: str):
    """
    Hashes a password using bcrypt.

    Args:
        password (str): The plain-text password to be hashed.

    Returns:
        bytes: The hashed password as a bcrypt hash.
    """
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(BCRYPT_SALT))
    return password_hash

def sign_jwt(data: dict, expires_in: int = 3600):
    """
    Generates a JSON Web Token (JWT) for the given data with an expiration time.

    Args:
        data (dict): The payload to encode into the JWT.
        expires_in (int): Expiration time in seconds (default: 3600 seconds = 1 hour).

    Returns:
        str: The encoded JWT string.
    """
    exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=expires_in)
    payload = {**data, "exp": exp_time}
    encoded = jwt.encode(payload=payload, key=JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded


def verify_jwt(token: str):
    """Decodes and verifies a JWT token using the secret key and algorithm."""
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])