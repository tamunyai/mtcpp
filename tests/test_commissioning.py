from fastapi import status

from app.schemas.line import LineStatus


def test_commission_line(auth_client):
    # Create an account
    acc_response = auth_client.post(
        "/accounts",
        json={"full_name": "Commission User", "email": "commission@example.com", "phone": "123"},
    )

    assert acc_response.status_code == status.HTTP_200_OK
    account_id = acc_response.json()["id"]

    # Create a line for that account
    line_response = auth_client.post(
        f"/accounts/{account_id}/lines",
        json={"msisdn": "777888999", "plan_name": "Gold"},
    )

    assert line_response.status_code == status.HTTP_200_OK
    assert line_response.json()["status"] == LineStatus.PROVISIONED
    line_id = line_response.json()["id"]

    # Commission the line
    response = auth_client.post(f"/lines/{line_id}/commission")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == LineStatus.ACTIVE


def test_commission_active_line_fails(auth_client):
    # Create an account
    acc_response = auth_client.post(
        "/accounts", json={"full_name": "Double Test", "email": "double@test.com", "phone": "000"}
    )

    assert acc_response.status_code == status.HTTP_200_OK
    account_id = acc_response.json()["id"]

    # Create a line for that account
    line_response = auth_client.post(
        f"/accounts/{account_id}/lines", json={"msisdn": "111222333", "plan_name": "Premium"}
    )

    assert line_response.status_code == status.HTTP_200_OK
    assert line_response.json()["status"] == LineStatus.PROVISIONED
    line_id = line_response.json()["id"]

    # First Commission (Should succeed)
    first_commission_response = auth_client.post(f"/lines/{line_id}/commission")
    assert first_commission_response.status_code == status.HTTP_200_OK
    assert first_commission_response.json()["status"] == LineStatus.ACTIVE

    # Second Commission (Should fail)
    second_commission_response = auth_client.post(f"/lines/{line_id}/commission")

    # We expect a 400 Bad Request because the state transition is invalid
    assert second_commission_response.status_code == status.HTTP_400_BAD_REQUEST
