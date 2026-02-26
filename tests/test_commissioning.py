from fastapi import status

from app.schemas.line import LineStatus


def test_commission_line(admin_client):
    # Create an account
    acc_response = admin_client.post(
        "/accounts",
        json={"full_name": "Commission User", "email": "commission@example.com", "phone": "123"},
    )

    assert acc_response.status_code == status.HTTP_200_OK
    account_id = acc_response.json()["id"]

    # Create a line for that account
    line_response = admin_client.post(
        f"/accounts/{account_id}/lines", json={"msisdn": "777888999", "plan_name": "Gold"}
    )

    assert line_response.status_code == status.HTTP_200_OK
    assert line_response.json()["status"] == LineStatus.PROVISIONED
    line_id = line_response.json()["id"]

    # Commission the line
    commission_response = admin_client.post(f"/lines/{line_id}/commission")

    assert commission_response.status_code == status.HTTP_200_OK
    assert commission_response.json()["status"] == LineStatus.ACTIVE.value


def test_commissioning_rejects_invalid_transitions(admin_client):
    # Create an account
    acc_response = admin_client.post(
        "/accounts", json={"full_name": "Double Test", "email": "double@test.com", "phone": "000"}
    )

    assert acc_response.status_code == status.HTTP_200_OK
    account_id = acc_response.json()["id"]

    # Create a line for that account
    line_response = admin_client.post(
        f"/accounts/{account_id}/lines", json={"msisdn": "700800900", "plan_name": "P"}
    )

    assert line_response.status_code == status.HTTP_200_OK
    assert line_response.json()["status"] == LineStatus.PROVISIONED
    line_id = line_response.json()["id"]

    # First Commission (Should succeed)
    first_commission_response = admin_client.post(f"/lines/{line_id}/commission")
    assert first_commission_response.status_code == status.HTTP_200_OK
    assert first_commission_response.json()["status"] == LineStatus.ACTIVE

    # Second Commission (Should fail)
    second_commission_response = admin_client.patch(
        f"/lines/{line_id}/status", json={"status": LineStatus.PROVISIONED.value}
    )

    # We expect a 400 Bad Request because the state transition is invalid
    assert second_commission_response.status_code == status.HTTP_400_BAD_REQUEST


def test_concurrent_commission(admin_client):
    # Create an account
    acc_response = admin_client.post(
        "/accounts",
        json={"full_name": "Concurrent Test", "email": "concurrent@test.com", "phone": "222"},
    )

    assert acc_response.status_code == status.HTTP_200_OK
    account_id = acc_response.json()["id"]

    # Create a line for that account
    line_response = admin_client.post(
        f"/accounts/{account_id}/lines", json={"msisdn": "333444555", "plan_name": "Concurrent"}
    )

    assert line_response.status_code == status.HTTP_200_OK
    assert line_response.json()["status"] == LineStatus.PROVISIONED
    line_id = line_response.json()["id"]

    # Concurrently commission from two threads
    import threading

    results = [None, None]

    def call(i):
        results[i] = admin_client.post(f"/lines/{line_id}/commission")

    t1 = threading.Thread(target=call, args=(0,))
    t2 = threading.Thread(target=call, args=(1,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    responses = {r.status_code for r in results}  # type: ignore
    assert status.HTTP_200_OK in responses
    assert status.HTTP_400_BAD_REQUEST in responses
