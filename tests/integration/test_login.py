import pytest


@pytest.mark.asyncio
async def test_login_success(client, verified_test_user):

    test_user = {
        "email": verified_test_user["email"],
        "password": verified_test_user["password"],
    }

    response = client.post("/auth/login", json=test_user)

    assert response.status_code == 200
    data = response.json()
    assert "accessToken" in data["data"]
    assert "csrfToken" in data["data"]


@pytest.mark.asyncio
async def test_login_wrong_email(client, verified_test_user):

    test_user = {
        "email": "thisisinvalidemail@test.com",
        "password": verified_test_user["password"],
    }

    response = client.post("/auth/login", json=test_user)

    assert response.status_code == 401
    data = response.json()
    assert data["errors"] == "Invalid email or password"


@pytest.mark.asyncio
async def test_login_not_verified_user(client, test_user):

    test_user = {
        "email": test_user["email"],
        "password": test_user["password"],
    }

    response = client.post("/auth/login", json=test_user)

    assert response.status_code == 403
    data = response.json()
    assert (
        data["errors"]
        == "Account not verified. Please verify your email or request a new verification link."
    )
