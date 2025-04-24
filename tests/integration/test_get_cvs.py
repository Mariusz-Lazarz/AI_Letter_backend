from helpers.auth import sign_jwt
from config import JWT_ACCESS_TOKEN
from typing import List
from schemas.base import DataResponse
from schemas.cv import CvListItem


def test_get_cvs_success(client, verified_test_user):
    access_token = sign_jwt(
        {"id": verified_test_user["id"], "email": verified_test_user["email"]},
        JWT_ACCESS_TOKEN,
    )
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.get("/cvs", headers=headers)
    assert response.status_code == 200

    parsed_response = DataResponse[List[CvListItem]].model_validate(response.json())

    assert isinstance(parsed_response.data, list)
    for item in parsed_response.data:
        assert isinstance(item, CvListItem)


def test_get_cvs_no_user(client, verified_test_user):

    access_token = sign_jwt(
        {"id": verified_test_user["id"], "email": "fakeemail@test.com"},
        JWT_ACCESS_TOKEN,
    )
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.get("/cvs", headers=headers)

    assert response.status_code == 404
    assert response.json() == {"errors": "User not found"}
