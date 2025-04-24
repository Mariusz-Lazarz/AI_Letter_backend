import pytest
from fastapi import UploadFile, HTTPException
from unittest.mock import AsyncMock, patch, MagicMock
from helpers.validate_upload_file import validate_upload_file


@pytest.mark.asyncio
@patch("helpers.validate_upload_file.magic.from_buffer", return_value="application/pdf")
async def test_validate_upload_file_success(mock_magic):
    mock_file = MagicMock(spec=UploadFile)
    mock_file.content_type = "application/pdf"
    mock_file.read = AsyncMock(return_value=b"%PDF-1.4 valid content")
    mock_file.seek = AsyncMock()

    result = await validate_upload_file(mock_file)

    assert result == b"%PDF-1.4 valid content"
    mock_file.seek.assert_called_once_with(0)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "content, content_type, fake_mime, expected_error",
    [
        (
            b"%PDF valid content",
            "image/png",
            "application/pdf",
            "Only PDF files are allowed.",
        ),
        (
            b"a" * (6 * 1024 * 1024),
            "application/pdf",
            "application/pdf",
            "File size exceeds",
        ),
        (
            b"%PDF-1.4 fake content",
            "application/pdf",
            "application/octet-stream",
            "not a valid PDF",
        ),
    ],
)
@patch("helpers.validate_upload_file.magic.from_buffer")
async def test_validate_upload_file_errors(
    mock_magic, content, content_type, fake_mime, expected_error
):
    mock_magic.return_value = fake_mime

    mock_file = MagicMock(spec=UploadFile)
    mock_file.content_type = content_type
    mock_file.read = AsyncMock(return_value=content)
    mock_file.seek = AsyncMock()

    with pytest.raises(HTTPException) as e:
        await validate_upload_file(mock_file)

    assert e.value.status_code == 400
    assert expected_error in e.value.detail
