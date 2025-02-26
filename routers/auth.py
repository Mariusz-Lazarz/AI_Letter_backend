from fastapi import APIRouter, Depends, Request, Query, HTTPException
from schemas.user import UserCreate, UserBase
from models.user import User
from database import SessionDep
from helpers.auth import hash_password, sign_jwt, verify_jwt
from helpers.email_sender import EmailSender
from helpers.limiter import RateLimiterService
from config import RATE_LIMIT_REGISTER, RATE_LIMIT_VERIFY, ACCOUNT_CONFIRMATION_TOKEN, RATE_LIMIT_RESEND_VERIFY
from sqlmodel import select
from helpers.logger import AppLogger

logger = AppLogger(log_file="app.log")

email_sender = EmailSender()
limiter = RateLimiterService()

router = APIRouter(prefix="/auth")

@router.post("/register", status_code=201)
@limiter.limit(RATE_LIMIT_REGISTER)
async def register(request: Request, user_data: UserCreate, session: SessionDep):
    try:
        verification_token = sign_jwt({"email": user_data.email}, expires_in=(ACCOUNT_CONFIRMATION_TOKEN))
        password_hash = hash_password(user_data.password)
        user = User(email=user_data.email, password_hash=password_hash, verification_token=verification_token)
        session.add(user)
        session.commit()
        session.refresh(user)

        email_sent = email_sender.account_confirmation(to_email=user.email, verification_token=verification_token)
        if not email_sent:
            logger.log_warning(f"⚠️ Email failed for {user.email}. User was created.")

        return {"data": {"message": "User created successfully"}}     
    except:
        session.rollback()
        raise

@router.get("/verify/", status_code=200)
@limiter.limit(RATE_LIMIT_VERIFY, key_func=lambda request: request.query_params.get("token", ""))
async def verify(request: Request, session: SessionDep,  token: str):
    try:
        verified_token = verify_jwt(token=token)
        user_email = verified_token.get("email")

        if not user_email:
            raise HTTPException(status_code=400, detail="Invalid token: Email missing")
        
        statement = select(User).where(User.email == user_email)
        result = session.exec(statement)
        user = result.first()

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        if user.verification_token != token:
            raise HTTPException(status_code=403, detail="Invalid verification token")

        if not user.is_verified:
            user.is_verified = True
            user.verification_token = ""
            session.add(user)
            session.commit()
            session.refresh(user)

        return {"data": {"message": "User verified successfully", "is_verified": True}}

    except Exception as e:
        session.rollback()
        logger.log_exception(f"Verification failed for {user_email if 'user_email' in locals() else 'Unknown'}: {e}")
        raise HTTPException(status_code=400, detail="Failed to verify user")


@router.post("/resend-verification-token", status_code=200)
@limiter.limit(RATE_LIMIT_RESEND_VERIFY)
async def resend_verification_token(request: Request, session: SessionDep, user_data: UserBase):
    try:
        statement = select(User).where(User.email == user_data.email)
        user = session.exec(statement).first()

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        if user.is_verified:
            return {"data": {"message": "User is already verified"}}

        verification_token = sign_jwt({"email": user_data.email}, expires_in=ACCOUNT_CONFIRMATION_TOKEN)
        user.verification_token = verification_token

        session.add(user)
        session.commit()
        session.refresh(user)

        email_sent = email_sender.account_confirmation(to_email=user_data.email, verification_token=verification_token)
        if not email_sent:
            logger.warning(f"⚠️ Email failed for {user_data.email}.")

        return {"data": {"message": "Verification email sent successfully"}}
    except HTTPException as e:
        raise
    except Exception as e:
        session.rollback()
        logger.log_exception(f"Verification failed for {user_data.email}: {e}")
        raise