from models.user import UserCV
from sqlmodel import select, delete, Session
from database import engine
from config import S3_BUCKET_NAME
from helpers.auth import sign_jwt
from config import JWT_ACCESS_TOKEN
from services.s3 import delete_from_s3
import io


def test_upload_cv_success(client, verified_test_user):
    file_content = b"%PDF-1.4 fake PDF content for integration"
    file = ("cv.pdf", io.BytesIO(file_content), "application/pdf")

    access_token = sign_jwt(
        {"id": verified_test_user["id"], "email": verified_test_user["email"]},
        JWT_ACCESS_TOKEN
    )
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.post(
        "/cvs",
        files={"file": file},
        headers=headers
    )

    assert response.status_code == 200
    assert response.json() == {"message": "CV uploaded successfully"}

    with Session(engine) as session:
        stmt = select(UserCV).where(
            (UserCV.user_id == verified_test_user["id"]) &
            (UserCV.original_name == "cv.pdf")
        )
        uploaded_cv = session.exec(stmt).first()
        assert uploaded_cv is not None

        print("Uploaded S3 Key:", uploaded_cv.s3_key)


        delete_from_s3(uploaded_cv.s3_key)

        session.exec(delete(UserCV).where(UserCV.user_id == verified_test_user["id"]))
        session.commit()


def test_upload_cv_fail(client, verified_test_user):
    file_content = b"%PDF-1.4 fake PDF content for integration"
    file = ("cv.pdf", io.BytesIO(file_content), "wrong type")

    access_token = sign_jwt(
        {"id": verified_test_user["id"], "email": verified_test_user["email"]},
        JWT_ACCESS_TOKEN
    )
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.post(
        "/cvs",
        files={"file": file},
        headers=headers
    )

    assert response.status_code == 400
    assert response.json() == {"errors": "Only PDF files are allowed."}
