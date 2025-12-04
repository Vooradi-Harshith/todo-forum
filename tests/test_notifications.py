# tests/test_notifications.py

import pytest
from tests.factories import create_user, create_notification


@pytest.mark.asyncio
async def test_notifications_endpoints(async_client, db_session):
    user = create_user(db_session, username="notifuser")
    create_notification(db_session, user.id)
    create_notification(db_session, user.id)

    # login
    res = await async_client.post("/auth/token", json={
        "username": "notifuser",
        "password": "pass123"
    })
    token = res.json()["access_token"]

    res2 = await async_client.get("/notifications/", headers={
        "Authorization": f"Bearer {token}"
    })
    assert res2.status_code == 200
    assert res2.json()["total"] >= 2

    # mark one read
    first = res2.json()["items"][0]["id"]
    res3 = await async_client.put(f"/notifications/{first}/read", headers={
        "Authorization": f"Bearer {token}"
    })
    assert res3.status_code == 200
    assert res3.json()["read"] is True
