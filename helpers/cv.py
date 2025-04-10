from fastapi import HTTPException
import io 
import fitz
from fpdf import FPDF
import os


def get_user_cv_by_id(user, cv_id):
    selected_cv = next((cv for cv in user.cvs if cv.id == cv_id), None)
    if selected_cv is None:
        raise HTTPException(status_code=404, detail="CV not found")
    return selected_cv

def extract_text_from_pdf(binary_pdf):
    pdf_stream = io.BytesIO(binary_pdf)
    doc = fitz.open(stream=pdf_stream, filetype="pdf")
    return "".join([page.get_text() for page in doc])


def convert_text_to_pdf(letter_content):
    pdf = FPDF()
    pdf.add_page()

    font_path = os.path.join("fonts", "DejaVuSans.ttf")
    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.set_font("DejaVu", size=12)

    for line in letter_content.split('\n'):
        pdf.multi_cell(0, 10, line)

    pdf_bytes = pdf.output(dest='S').encode('latin1')

    return pdf_bytes
