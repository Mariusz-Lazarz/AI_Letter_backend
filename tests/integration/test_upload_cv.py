from models.user import UserCV
from sqlmodel import select, delete, Session
from database import engine
import boto3
from config import S3_BUCKET_NAME
from helpers.auth import sign_jwt
from config import JWT_ACCESS_TOKEN
import io

def delete_s3_file(s3_key: str):
    s3 = boto3.client("s3")
    s3.delete_object(Bucket=S3_BUCKET_NAME, Key=s3_key)


def test_upload_cv_success(client, verified_test_user):
    file_content = b"%PDF-1.4 fake PDF content for integration"
    file = ("cv.pdf", io.BytesIO(file_content), "application/pdf")

    access_token = sign_jwt(
        {"id": verified_test_user["id"], "email": verified_test_user["email"]},
        JWT_ACCESS_TOKEN
    )
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.post(
        "/cv/upload-cv",
        files={"file": file},
        headers=headers
    )

    assert response.status_code == 200
    assert response.json() == {"message": "CV uploaded successfully"}

    with Session(engine) as session:
        stmt = select(UserCV).where(UserCV.user_id == verified_test_user["id"])
        uploaded_cv = session.exec(stmt).first()
        assert uploaded_cv is not None

        delete_s3_file(uploaded_cv.s3_key)

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
        "/cv/upload-cv",
        files={"file": file},
        headers=headers
    )

    assert response.status_code == 400
    assert response.json() == {"errors": "Only PDF files are allowed."}



