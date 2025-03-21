import pytest


@pytest.mark.asyncio
async def test_forgot_password_existing_user(client, verified_test_user):

    test_user = {"email": verified_test_user["email"]}

    response = client.post("/auth/forgot_password", json=test_user)
    assert response.status_code == 201
    data = response.json()
    assert (
        data["data"]["message"]
        == "If an account is associated with this email, you will receive an email shortly."
    )


@pytest.mark.asyncio
async def test_forgot_password_non_existing_user(client):
    test_user = {"email": "thisemaildoesnotexist@test.com"}
    response = client.post("/auth/forgot_password", json=test_user)
    assert response.status_code == 201
    data = response.json()
    assert (
        data["data"]["message"]
        == "If an account is associated with this email, you will receive an email shortly."
    )
