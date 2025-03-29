from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from helpers.auth import verify_jwt

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    verified_token = verify_jwt(token=token)

    if verified_token:
        return verified_token
