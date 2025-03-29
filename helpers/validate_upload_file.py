from fastapi import UploadFile, HTTPException
from config import ALLOWED_MIME_TYPES, MAX_FILE_SIZE_MB
import magic

async def validate_upload_file(file: UploadFile):
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