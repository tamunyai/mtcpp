from fastapi import status

from app.schemas.line import LineStatus


def test_create_line(auth_client):
    # Create an account
    acc_response = auth_client.post(
        "/accounts",
        json={"full_name": "Line Owner", "email": "line@example.com", "phone": "555111"},
    )

    assert acc_response.status_code == status.HTTP_200_OK
    account_id = acc_response.json()["id"]

    response = auth_client.post(
        f"/accounts/{account_id}/lines",
        json={"msisdn": "999000111", "plan_name": "Basic Plan"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == LineStatus.PROVISIONED
