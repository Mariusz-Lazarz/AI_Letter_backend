import magic
import uuid
import urllib.parse
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request
from sqlmodel import select
from database import SessionDep
from middleware.verify_user import verify_token
from config import MAX_FILE_SIZE_MB, ALLOWED_MIME_TYPES
from services.s3 import upload_to_s3
from models.user import User, UserCV

router = APIRouter(prefix="/cv", dependencies=[Depends(verify_token)])

async def validate_uploaded_file(file: UploadFile):
    if file.content_type not in ALLOWED_MIME_TYPES:
         raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    content = await file.read()

    file_size_mb = len(content) / (1024 * 1024)

    if file_size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds {MAX_FILE_SIZE_MB}MB limit.",
        )
    mime = magic.from_buffer(content, mime=True)
    if mime != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is not a valid PDF.",
        )

    await file.seek(0)

    return content


@router.post("/upload-cv", status_code=200)
async def upload_file(request: Request, session: SessionDep, file: UploadFile = File(...), user=Depends(verify_token)):
    try:
        content = await validate_uploaded_file(file)

        safe_filename = urllib.parse.quote_plus(file.filename)
        file_uuid = str(uuid.uuid4())
        s3_key = f"{file_uuid}.pdf"

        tagging_str = f"original_name={safe_filename}"

        uploaded_file = upload_to_s3(content, s3_key, "application/pdf", tagging_str)

        if not uploaded_file:
            raise HTTPException(status_code=502, detail=f"Failed to upload a file")
        
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
