from fastapi import status

from app.schemas.account import AccountStatus


def test_create_account(admin_client):
    acc_response = admin_client.post(
        "/accounts",
        json={
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "123456789",
        },
    )

    assert acc_response.status_code == status.HTTP_200_OK

    data = acc_response.json()
    assert data["email"] == "test@example.com"
    assert data["status"] == AccountStatus.ACTIVE.value


def test_create_account_duplicate_email(admin_client):
    payload = {"full_name": "Duplicate User", "email": "dup@example.com", "phone": "123"}

    first_acc_response = admin_client.post("/accounts", json=payload)

    assert first_acc_response.status_code == status.HTTP_200_OK

    # Second request with same email
    second_acc_response = admin_client.post("/accounts", json=payload)

    assert second_acc_response.status_code == status.HTTP_409_CONFLICT


def test_invalid_email_account(admin_client):
    acc_response = admin_client.post(
        "/accounts",
        json={"full_name": "Bad Email", "email": "not-an-email", "phone": "123456789"},
    )

    assert acc_response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_invalid_uuid_returns_422(admin_client):
    acc_response = admin_client.get("/accounts/not-a-uuid")

    assert acc_response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_operator_can_list_accounts(operator_client):
    acc_response = operator_client.get("/accounts")

    assert acc_response.status_code == status.HTTP_200_OK


def test_operator_cannot_update_account(operator_client, admin_client):
    # Create an account as admin
    payload = {"full_name": "To Update", "email": "to-update@example.com", "phone": "000"}
    acc_response = admin_client.post("/accounts", json=payload)

    assert acc_response.status_code == status.HTTP_200_OK
    account_id = acc_response.json()["id"]

    # Operator attempts to update
    acc_response = operator_client.put(f"/accounts/{account_id}", json={"full_name": "Hacked"})
    assert acc_response.status_code == status.HTTP_403_FORBIDDEN
