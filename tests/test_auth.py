from fastapi import status


def test_login_success(client):
    response = client.post("/auth/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()


def test_login_failure(client):
    response = client.post("/auth/login", json={"username": "admin", "password": "wrongpass"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
