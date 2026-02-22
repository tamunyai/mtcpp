from fastapi import status

from app.schemas.account import AccountStatus


def test_create_account(auth_client):
    response = auth_client.post(
        "/accounts",
        json={
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "123456789",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["status"] == AccountStatus.ACTIVE


def test_invalid_email_account(auth_client):
    response = auth_client.post(
        "/accounts",
        json={"full_name": "Bad Email", "email": "not-an-email", "phone": "123456789"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
