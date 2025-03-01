import pytest
from helpers.auth import sign_jwt
from config import JWT_ACCESS_TOKEN


@pytest.mark.asyncio
async def test_login_success(client, verified_test_user):

    test_user = {
        "email": verified_test_user["email"],
        "password": verified_test_user["password"]
    }

    response = client.post("/auth/login", json=test_user)

    assert response.status_code == 200
    data = response.json()
    assert "token" in data["data"]

@pytest.mark.asyncio
async def test_login_wrong_email(client, verified_test_user):

    test_user = {
        "email": "thisisinvalidemail@test.com",
        "password": verified_test_user["password"]
    }

    response = client.post("/auth/login", json=test_user)

    assert response.status_code == 401
    data = response.json()
    assert data["errors"][0] == "Invalid email or password"

@pytest.mark.asyncio
async def test_login_not_verified_user(client, test_user):

    test_user = {
        "email": test_user["email"],
        "password": test_user["password"]
    }

    response = client.post("/auth/login", json=test_user)

    assert response.status_code == 403
    data = response.json()
    assert data["errors"][0] == "Account not verified. Please verify your email or request a new verification link."