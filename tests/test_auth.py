from fastapi import status


def test_login_success(client):
    response = client.post("/auth/login", json={"username": "admin", "password": "admin123"})

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()


def test_login_failure(client):
    response = client.post("/auth/login", json={"username": "admin", "password": "wrongpass"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_operator_cannot_create_resources(operator_client, admin_client):
    # Operator cannot create accounts
    acc_response = operator_client.post(
        "/accounts", json={"full_name": "A", "email": "a@example.com", "phone": "1"}
    )

    assert acc_response.status_code == status.HTTP_403_FORBIDDEN

    # Admin prepares account; operator cannot create lines for it
    acc_response = admin_client.post(
        "/accounts", json={"full_name": "Owner", "email": "owner@example.com", "phone": "0"}
    )
    account_id = acc_response.json()["id"]

    line_response = operator_client.post(
        f"/accounts/{account_id}/lines", json={"msisdn": "999000111", "plan_name": "Basic"}
    )

    assert line_response.status_code == status.HTTP_403_FORBIDDEN
