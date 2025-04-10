from helpers.auth import sign_jwt
from unittest.mock import patch
from config import JWT_ACCESS_TOKEN
import pytest
import uuid


@pytest.mark.asyncio
@patch("routers.letter.get_from_s3")
async def test_generate_letter_success(mock_s3, client, verified_test_user):
    access_token = sign_jwt(
        {"id": verified_test_user["id"], "email": verified_test_user["email"]},
        JWT_ACCESS_TOKEN,
    )
    headers = {"Authorization": f"Bearer {access_token}"}

    letter_data = {
        "cv_id": str(verified_test_user["user_cv_id"]),
        "job_desc": (
            "50charslong50charslong50charslong50charslong50charslong"
            "50charslong50charslong50charslong50charslong50charslong"
            "50charslong50charslong50charslong50charslong50charslong"
            "50charslong50charslong50charslong50charslong50charslong"
            "50charslong"
        ),
    }

    mock_s3.return_value = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<<>>\nendobj\n"
        b"xref\n0 2\n0000000000 65535 f \n0000000010 00000 n \n"
        b"trailer\n<< /Root 1 0 R >>\nstartxref\n9\n%%EOF"
    )

    response = client.post("/letter", headers=headers, json=letter_data)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-disposition"] == "attachment; filename=cover_letter.pdf"
    assert response.content.startswith(b"%PDF")


@pytest.mark.asyncio
async def test_generate_letter_no_user(client, verified_test_user):
    access_token = sign_jwt(
        {"id": verified_test_user["id"], "email": "fakeemail.com"},
        JWT_ACCESS_TOKEN,
    )
    headers = {"Authorization": f"Bearer {access_token}"}

    letter_data = {
        "cv_id": str(verified_test_user["user_cv_id"]),
        "job_desc": (
            "50charslong50charslong50charslong50charslong50charslong"
            "50charslong50charslong50charslong50charslong50charslong"
            "50charslong50charslong50charslong50charslong50charslong"
            "50charslong50charslong50charslong50charslong50charslong"
            "50charslong"
        ),
    }

    response = client.post("/letter", headers=headers, json=letter_data)

    assert response.status_code == 404
    assert response.json() == {"errors": "User not found"}


@pytest.mark.asyncio
async def test_generate_letter_no_cv_in_db(client, verified_test_user):
    access_token = sign_jwt(
        {"id": verified_test_user["id"], "email": verified_test_user["email"]},
        JWT_ACCESS_TOKEN,
    )
    headers = {"Authorization": f"Bearer {access_token}"}

    letter_data = {
        "cv_id": str(uuid.uuid4()),
        "job_desc": (
            "50charslong50charslong50charslong50charslong50charslong"
            "50charslong50charslong50charslong50charslong50charslong"
            "50charslong50charslong50charslong50charslong50charslong"
            "50charslong50charslong50charslong50charslong50charslong"
            "50charslong"
        ),
    }

    response = client.post("/letter", headers=headers, json=letter_data)

    assert response.status_code == 404
    assert response.json() == {"errors": "CV not found"}
