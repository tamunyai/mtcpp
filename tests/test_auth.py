from datetime import timedelta

from fastapi import status

from app.core.security import create_access_token


def test_unauthenticated_access_denied(client):
    response = client.get("/accounts/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_success(client):
    response = client.post("/auth/login", json={"username": "admin_test", "password": "admin123"})

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

    assert acc_response.status_code == status.HTTP_200_OK
    account_id = acc_response.json()["id"]

    line_response = operator_client.post(
        f"/accounts/{account_id}/lines", json={"msisdn": "999000111", "plan_name": "Basic"}
    )

    assert line_response.status_code == status.HTTP_403_FORBIDDEN


def test_expired_token_returns_401(client):
    token, _ = create_access_token(
        {"sub": "admin_test", "role": "ADMIN"}, expires_delta=timedelta(seconds=-10)
    )

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/accounts", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_malformed_and_tampered_token_returns_401(client, admin_token):
    # Malformed token
    response = client.get("/accounts", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Tampered token
    tampered = admin_token[:-1] + ("a" if admin_token[-1] != "a" else "b")
    response = client.get("/accounts", headers={"Authorization": f"Bearer {tampered}"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
