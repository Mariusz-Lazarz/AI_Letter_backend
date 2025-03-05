import pytest
from helpers.auth import sign_jwt
from config import JWT_REFRESH_EXPIRE

@pytest.mark.asyncio
async def test_refresh_token_success(client, verified_test_user):

    user_id = "123"
    user_email = verified_test_user["email"]

    csrf_token = "valid-csrf-token-example"
    refresh_token = sign_jwt(
        {"id": user_id, "email": user_email, "csrfToken": csrf_token},
        JWT_REFRESH_EXPIRE
    )


    client.cookies.set("refresh_token", refresh_token)

    response = client.post("/auth/refresh-token", headers={"X-CSRF-Token": csrf_token})

    assert response.status_code == 200
    data = response.json()
    assert "accessToken" in data["data"]
    

@pytest.mark.asyncio
async def test_no_refresh_token(client):
    refresh_token = None
    client.cookies.set("refresh_token", refresh_token)
    response = client.post("/auth/refresh-token")

    assert response.status_code == 401
    data = response.json()
    assert data["errors"][0] == "Unauthorized"

@pytest.mark.asyncio
async def test_csrf_token_dont_match(client, verified_test_user):
    
    user_id = "123"
    user_email = verified_test_user["email"]

    valid_csrf_token = "valid-csrf-token-example"
    invalid_csrf_token = "invalid-csrf-token-example"
    refresh_token = sign_jwt(
        {"id": user_id, "email": user_email, "csrfToken": valid_csrf_token},
        JWT_REFRESH_EXPIRE
    )


    client.cookies.set("refresh_token", refresh_token)

    response = client.post("/auth/refresh-token", headers={"X-CSRF-Token": invalid_csrf_token})

    assert response.status_code == 401
    data = response.json()
    assert data["errors"][0] == "Unauthorized"