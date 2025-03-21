import pytest


@pytest.mark.asyncio
async def test_resend_token_success(client, test_user):

    email = {"email": test_user["email"]}

    response = client.post("/auth/resend-verification-token", json=email)

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["message"] == "Verification email sent successfully"


@pytest.mark.asyncio
async def test_resend_token_invalid_email(client, test_user):

    email = {"email": "thisisinvalidemail@test.com"}

    response = client.post("/auth/resend-verification-token", json=email)

    assert response.status_code == 404
    data = response.json()
    assert data["errors"][0] == "User not found"


@pytest.mark.asyncio
async def test_resend_token_user_verified(client, verified_test_user):

    email = {"email": verified_test_user["email"]}

    response = client.post("/auth/resend-verification-token", json=email)

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["message"] == "User is already verified"
