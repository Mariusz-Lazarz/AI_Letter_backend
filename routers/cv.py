import magic
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from middleware.verify_user import verify_token
from config import MAX_FILE_SIZE_MB, ALLOWED_MIME_TYPES

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


@router.post("/upload-cv")
async def upload_file(file: UploadFile = File(...), user=Depends(verify_token)):
    content = await validate_uploaded_file(file)
    return {"filename": file.filename, "size_kb": len(content) / 1024}
