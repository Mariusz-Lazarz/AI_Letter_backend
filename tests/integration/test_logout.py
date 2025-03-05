import pytest
from helpers.auth import sign_jwt
from config import JWT_REFRESH_EXPIRE


@pytest.mark.asyncio
async def test_logout_success(client, verified_test_user):
    
    id = "123"
    email = verified_test_user["email"]
    
    refresh_token = sign_jwt({"id": id, "email": email, "csrfToken": "abc"})

    client.cookies.set("refresh_token", refresh_token)

    response = client.post("/auth/logout")

    assert response.cookies.get("refresh_token") is None
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_logout_no_refresh_token(client):
    refresh_token = None
    client.cookies.set("refresh_token", refresh_token)

    response = client.post("/auth/logout")

    assert response.status_code == 403
    data = response.json()
    assert data["errors"][0] == "Forbidden"