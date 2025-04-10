from unittest.mock import patch, MagicMock
from helpers.cv import extract_text_from_pdf


@patch("helpers.cv.fitz.open")
def test_extract_text_from_pdf(mock_fitz_open):
    mock_page1 = MagicMock()
    mock_page1.get_text.return_value = "Hello "
    mock_page2 = MagicMock()
    mock_page2.get_text.return_value = "World!"

    mock_doc = [mock_page1, mock_page2]
    mock_fitz_open.return_value = mock_doc

    fake_binary_pdf = b"%PDF-1.4 fake content here"

    result = extract_text_from_pdf(fake_binary_pdf)

    assert result == "Hello World!"

    mock_fitz_open.assert_called_once()
