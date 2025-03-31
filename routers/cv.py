
import uuid
import urllib.parse
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request
from sqlmodel import select
from config import RATE_LIMIT_UPLOAD_CV
from database import SessionDep
from middleware.verify_user import verify_token
from services.s3 import upload_to_s3
from models.user import User, UserCV
from helpers.validate_upload_file import validate_upload_file
from helpers.limiter import RateLimiterService

limiter = RateLimiterService()

router = APIRouter(prefix="/cv", dependencies=[Depends(verify_token)])


@router.post("/upload-cv", status_code=200)
@limiter.limit(RATE_LIMIT_UPLOAD_CV)
async def upload_file(request: Request, session: SessionDep, file: UploadFile = File(...), user=Depends(verify_token)):
    try:
        content = await validate_upload_file(file)

        safe_filename = urllib.parse.quote_plus(file.filename)
        file_uuid = str(uuid.uuid4())
        s3_key = f"{file_uuid}.pdf"

        tagging_str = f"original_name={safe_filename}"

        uploaded_file = upload_to_s3(content, s3_key, "application/pdf", tagging_str)

        if not uploaded_file:
            raise HTTPException(status_code=502, detail="Failed to upload a file")
        statement = select(User).where(User.email == user["email"])
        db_user = session.exec(statement).first()

        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        user_cv = UserCV(
            id=file_uuid,
            user_id=user["id"],
            s3_key=s3_key,
            original_name=safe_filename,
        )

        session.add(user_cv)
        session.commit()
        return {
            "message": "CV uploaded successfully",
        }

    except Exception:
        session.rollback()
        raise
