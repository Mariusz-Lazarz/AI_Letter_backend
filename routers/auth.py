from fastapi import APIRouter, Request, HTTPException, Response, BackgroundTasks
from schemas.user import UserCreate, UserBase, UserLogin, UserPasswordReset
from models.user import User
from database import SessionDep
from helpers.auth import hash_password, sign_jwt, verify_jwt, compare_password
from helpers.email_sender import EmailSender
from helpers.limiter import RateLimiterService
from config import JWT_ACCESS_TOKEN, JWT_REFRESH_EXPIRE, RATE_LIMIT_LOGIN, RATE_LIMIT_REFRESH_TOKEN, RATE_LIMIT_REGISTER, RATE_LIMIT_VERIFY, ACCOUNT_CONFIRMATION_TOKEN, RATE_LIMIT_RESEND_VERIFY, RESET_PASSWORD_TOKEN, RATE_LIMIT_FORGOT_PASSWORD, RATE_LIMIT_RESET_PASSWORD
from sqlmodel import select
from helpers.logger import AppLogger
import uuid

logger = AppLogger(log_file="app.log")

email_sender = EmailSender()
limiter = RateLimiterService()

router = APIRouter(prefix="/auth")

@router.post("/register", status_code=201)
@limiter.limit(RATE_LIMIT_REGISTER)
async def register(request: Request, user_data: UserCreate, session: SessionDep, background_tasks: BackgroundTasks):
    try:
        verification_token = sign_jwt({"email": user_data.email}, expires_in=(ACCOUNT_CONFIRMATION_TOKEN))
        password_hash = hash_password(user_data.password)
        user = User(email=user_data.email, password_hash=password_hash, verification_token=verification_token)
        session.add(user)
        session.commit()
        session.refresh(user)

        background_tasks.add_task(email_sender.account_confirmation, to_email=user.email, verification_token=verification_token)

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
            user.verification_token = None
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
async def resend_verification_token(request: Request, session: SessionDep, user_data: UserBase, background_tasks: BackgroundTasks):
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

        background_tasks.add_task(email_sender.account_confirmation, to_email=user.email, verification_token=verification_token)

        return {"data": {"message": "Verification email sent successfully"}}
    except HTTPException as e:
        raise
    except Exception as e:
        session.rollback()
        logger.log_exception(f"Verification failed for {user_data.email}: {e}")
        raise

@router.post("/login", status_code=200)
@limiter.limit(RATE_LIMIT_LOGIN)
async def login(request: Request,response: Response,  session: SessionDep, user_data: UserLogin):
    try:
        statement = select(User).where(User.email == user_data.email)
        user = session.exec(statement).first()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        checked_password = compare_password(user_data.password, user.password_hash)
        
        if not checked_password:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        if not user.is_verified:
            raise HTTPException(
                status_code=403, 
                detail="Account not verified. Please verify your email or request a new verification link."
            )

        csrfToken = str(uuid.uuid4())
        
        refresh_token = sign_jwt({"id": user.id, "email": user.email, "csrfToken": csrfToken}, JWT_REFRESH_EXPIRE)
        access_token = sign_jwt({"id": user.id, "email": user.email}, JWT_ACCESS_TOKEN)
        response.set_cookie(key="refresh_token", value=refresh_token, max_age=JWT_REFRESH_EXPIRE, httponly=True, secure=True, samesite="strict")
        return {"data": {"accessToken": access_token, "csrfToken": csrfToken}}
    except HTTPException as e:
        raise
    except Exception as e:
        session.rollback()
        logger.log_exception(f"Verification failed for {user_data.email}: {e}")
        raise


@router.post("/refresh-token", status_code=200)
@limiter.limit(RATE_LIMIT_REFRESH_TOKEN)
async def refresh_token(request: Request):
   try:
        refresh_token = request.cookies.get("refresh_token")

        if not refresh_token:
            raise HTTPException(status_code=401, detail="Unauthorized")

        verified_token = verify_jwt(token=refresh_token)
        csrf_token = verified_token.get("csrfToken")
        csrf_header_token = request.headers.get("X-CSRF-Token")

        if csrf_token != csrf_header_token:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        id = verified_token.get("id")
        email = verified_token.get("email")
        access_token = sign_jwt({"id": id, "email": email}, JWT_ACCESS_TOKEN)

        return {"data": {"accessToken": access_token}}

   except Exception as e:
        raise

@router.post("/logout", status_code=204)
async def logout(request: Request, response: Response):
    try:
        refresh_token = request.cookies.get("refresh_token")

        if not refresh_token:
            raise HTTPException(status_code=403, detail="Forbidden")
        
        response.delete_cookie("refresh_token")
    
    except Exception as e:
        raise
    

@router.post("/forgot_password", status_code=201)
@limiter.limit(RATE_LIMIT_FORGOT_PASSWORD)
async def forgot_password(request: Request, session: SessionDep, user_data: UserBase, background_tasks: BackgroundTasks):
    try:
        statement = select(User).where(User.email == user_data.email)
        user = session.exec(statement).first()
        if user:
            password_reset_token = sign_jwt({"email": user.email}, RESET_PASSWORD_TOKEN)
            user.password_reset_token = password_reset_token
            session.add(user)
            session.commit()
            background_tasks.add_task(email_sender.forgot_password, to_email=user.email, password_reset_token=password_reset_token)
    except Exception as e:
        raise
    return {"data": {"message": "If an account is associated with this email, you will receive an email shortly."}} 


@router.post("/reset_password", status_code=200)
@limiter.limit(RATE_LIMIT_RESET_PASSWORD)
async def reset_password(request: Request, session: SessionDep, user_data: UserPasswordReset):
    try:
        verified_token = verify_jwt(token=user_data.token)
        
        email = verified_token.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token: Email missing")
            
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        if not user or user.password_reset_token != user_data.token:
            raise HTTPException(status_code=401, detail="Unauthorized")
            
        password_hash = hash_password(user_data.password)
        user.password_hash = password_hash
        user.password_reset_token = None
        session.add(user)
        session.commit()
        
        return {"data": {"message": "Password reset successful"}}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.log_exception(f"Password reset failed: {e}")
        raise    
    