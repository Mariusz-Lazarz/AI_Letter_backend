from fastapi import APIRouter, Depends, Request
from schemas.user import UserCreate
from models.user import User
from database import SessionDep
from helpers.auth import hash_password, sign_jwt
from helpers.email_sender import EmailSender
from helpers.limiter import RateLimiterService
from config import RATE_LIMIT_REGISTER

email_sender = EmailSender()
limiter = RateLimiterService()

router = APIRouter(prefix="/auth")

@router.post("/register", status_code=201)
@limiter.limit(RATE_LIMIT_REGISTER)
async def register(request: Request, user_data: UserCreate, session: SessionDep):
    try:
        verification_token = sign_jwt({"email": user_data.email})
        password_hash = hash_password(user_data.password)
        user = User(email=user_data.email, password_hash=password_hash, verification_token=verification_token)
        session.add(user)
        session.commit()
        session.refresh(user)

        email_sent = email_sender.account_confirmation(to_email=user.email, verification_token=verification_token)
        if not email_sent:
            print(f"⚠️ Email failed for {user.email}. User was created.")

        return {"data": {"message": "User created successfully"}}     
    except:
        session.rollback()
        raise
  