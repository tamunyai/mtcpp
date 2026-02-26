from fastapi import status

from app.schemas.line import LineStatus


def test_create_line(admin_client):
    # Create an account
    acc_response = admin_client.post(
        "/accounts",
        json={"full_name": "Line Owner", "email": "line@example.com", "phone": "555111"},
    )

    assert acc_response.status_code == status.HTTP_200_OK
    account_id = acc_response.json()["id"]

    # Create a line for that account
    line_response = admin_client.post(
        f"/accounts/{account_id}/lines", json={"msisdn": "999000111", "plan_name": "Basic Plan"}
    )

    assert line_response.status_code == status.HTTP_200_OK
    assert line_response.json()["status"] == LineStatus.PROVISIONED.value
