from fastapi import APIRouter, Depends, Request, HTTPException, Response
from middleware.verify_user import verify_token
from database import SessionDep
from schemas.letter import GenerateCoverLetter
from services.s3 import get_from_s3
from helpers.cv import get_user_cv_by_id, extract_text_from_pdf, convert_text_to_pdf
from helpers.db import get_user_by_email
from services.client_openai import generate_cover_letter

router = APIRouter(prefix="/letter", dependencies=[Depends(verify_token)])


@router.post("/", status_code=200)
def generate_letter(request: Request, session: SessionDep, letter_data: GenerateCoverLetter, user=Depends(verify_token)):

    db_user = get_user_by_email(session, user)
    cv_id = letter_data.cv_id
    selected_cv = get_user_cv_by_id(db_user, cv_id)

    cv_binary = get_from_s3(selected_cv.s3_key)
    if not cv_binary:
        raise HTTPException(status_code=404, detail="CV not found")

    cv_text = extract_text_from_pdf(cv_binary)

    job_text = letter_data.job_desc

    letter_content = generate_cover_letter(cv=cv_text, job=job_text)

    pdf_bytes = convert_text_to_pdf(letter_content)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=cover_letter.pdf"
        }
    )
