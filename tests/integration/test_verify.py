import pytest
from helpers.auth import sign_jwt


@pytest.mark.asyncio
async def test_verify_success(client, test_user):
    """Test that a valid user can verify their account successfully."""
    token = test_user["verification_token"]

    response = client.get(f"/auth/verify/?token={token}")
    assert response.status_code == 200
    data = response.json()

    assert data["data"]["message"] == "User verified successfully"
    assert data["data"]["is_verified"] is True


@pytest.mark.asyncio
async def test_verify_missing_email(client):
    """Test that verification fails when the token has no email field."""

    invalid_token = sign_jwt({"user_id": 123})

    response = client.get(f"/auth/verify/?token={invalid_token}")

    assert response.status_code == 400
    data = response.json()
    assert data["errors"] == "Failed to verify user"


@pytest.mark.asyncio
async def test_user_not_found(client):
    invalid_token = sign_jwt({"email": "thisemaildoesnotexist@test.com"})

    response = client.get(f"/auth/verify/?token={invalid_token}")

    assert response.status_code == 400
    data = response.json()
    assert data["errors"] == "Failed to verify user"


@pytest.mark.asyncio
async def test_verify_token_mismatch(client, test_user):
    """Test that verification fails when the token does not match the stored one."""

    mismatched_token = sign_jwt({"email": test_user["email"]})

    response = client.get(f"/auth/verify/?token={mismatched_token}")

    assert response.status_code == 400
    data = response.json()
    assert data["errors"] == "Failed to verify user"


@pytest.mark.asyncio
async def test_verify_expired_token(client, test_user):
    """Test that verification fails when the token is expired."""

    expired_token = sign_jwt({"email": test_user["email"]}, expires_in=-10)

    response = client.get(f"/auth/verify/?token={expired_token}")

    assert response.status_code == 400
    data = response.json()
    assert data["errors"] == "Failed to verify user"
