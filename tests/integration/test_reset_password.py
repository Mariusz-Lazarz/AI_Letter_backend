import pytest
from helpers.auth import sign_jwt
from config import RESET_PASSWORD_TOKEN


@pytest.mark.asyncio
async def test_reset_password_success(client, verified_test_user):
    test_user = {
        "token": verified_test_user["password_reset_token"],
        "password": "Thisisvalid123!",
        "confirm_password": "Thisisvalid123!",
    }

    response = client.post("/auth/reset_password", json=test_user)
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["message"] == "Password reset successful"


@pytest.mark.asyncio
async def test_reset_password_no_email(client, verified_test_user):

    token = sign_jwt({"test": "test"}, RESET_PASSWORD_TOKEN)
    test_user = {
        "token": token,
        "password": "Thisisvalid123!",
        "confirm_password": "Thisisvalid123!",
    }

    response = client.post("/auth/reset_password", json=test_user)
    assert response.status_code == 400
    data = response.json()
    assert data["errors"] == "Invalid token: Email missing"


@pytest.mark.asyncio
async def test_reset_password_no_user(client):

    token = sign_jwt({"email": "test"}, RESET_PASSWORD_TOKEN)
    test_user = {
        "token": token,
        "password": "Thisisvalid123!",
        "confirm_password": "Thisisvalid123!",
    }

    response = client.post("/auth/reset_password", json=test_user)
    assert response.status_code == 401
    data = response.json()
    assert data["errors"] == "Unauthorized"


@pytest.mark.asyncio
async def test_reset_password_wrong_token(client, verified_test_user):

    password_reset_token = sign_jwt(
        {"email": verified_test_user["email"]}, RESET_PASSWORD_TOKEN
    )
    test_user = {
        "token": password_reset_token,
        "password": "Thisisvalid123!",
        "confirm_password": "Thisisvalid123!",
    }

    response = client.post("/auth/reset_password", json=test_user)
    assert response.status_code == 401
    data = response.json()
    assert data["errors"] == "Unauthorized"
