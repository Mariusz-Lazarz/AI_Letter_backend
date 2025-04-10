import pytest
from helpers.cv import convert_text_to_pdf


def test_convert_text_to_pdf():
    letter_content = "Test letter content\nTest new line"

    pdf_bytes = convert_text_to_pdf(letter_content)

    assert pdf_bytes.startswith(b"%PDF")
    assert isinstance(pdf_bytes, bytes)

