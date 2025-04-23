import uuid
import urllib.parse
from typing import List
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request
from config import RATE_LIMIT_UPLOAD_CV
from database import SessionDep
from middleware.verify_user import verify_token
from services.s3 import upload_to_s3, delete_from_s3
from models.user import UserCV
from helpers.validate_upload_file import validate_upload_file
from helpers.limiter import RateLimiterService
from schemas.cv import CvListItem
from schemas.base import DataResponse
from helpers.db import get_user_by_email

limiter = RateLimiterService()

router = APIRouter(prefix="/cvs", dependencies=[Depends(verify_token)])


@router.post("", status_code=200)
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
        get_user_by_email(session, user["email"])

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


@router.get("", status_code=200, response_model=DataResponse[List[CvListItem]])
async def get_cvs(request: Request, session: SessionDep, user=Depends(verify_token)):
    db_user = get_user_by_email(session, user["email"])
    return {"data": db_user.cvs}


@router.delete("", status_code=204)
async def delete_cv(request: Request, session: SessionDep, id: str, user=Depends(verify_token)):
    get_user_by_email(session, user["email"])

    user_cv = session.get(UserCV, id)

    if not user_cv:
        raise HTTPException(status_code=404, detail="Cv not found")

    delete_from_s3(key=user_cv.s3_key)

    session.delete(user_cv)
    session.commit()
