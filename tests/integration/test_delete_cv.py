import uuid
from helpers.auth import sign_jwt
from config import JWT_ACCESS_TOKEN


def test_delete_cv_success(client, verified_test_user):
    access_token = sign_jwt(
        {"id": verified_test_user["id"], "email": verified_test_user["email"]},
        JWT_ACCESS_TOKEN,
    )
    headers = {"Authorization": f"Bearer {access_token}"}

    params = {"id": verified_test_user["user_cv_id"]}

    response = client.delete("/cvs", headers=headers, params=params)
    assert response.status_code == 204


def test_delete_cv_no_user(client, verified_test_user):
    access_token = sign_jwt(
        {"id": verified_test_user["id"], "email": "thisemaildoesnotexist@test.com"},
        JWT_ACCESS_TOKEN,
    )
    headers = {"Authorization": f"Bearer {access_token}"}

    params = {"id": verified_test_user["user_cv_id"]}

    response = client.delete("/cvs", headers=headers, params=params)
    assert response.status_code == 404
    assert response.json() == {"errors": "User not found"}


def test_delete_cv_no_cv(client, verified_test_user):
    access_token = sign_jwt(
        {"id": verified_test_user["id"], "email": verified_test_user["email"]},
        JWT_ACCESS_TOKEN,
    )
    headers = {"Authorization": f"Bearer {access_token}"}

    params = {"id": uuid.uuid4()}

    response = client.delete("/cvs", headers=headers, params=params)
    assert response.status_code == 404
    assert response.json() == {"errors": "Cv not found"}
