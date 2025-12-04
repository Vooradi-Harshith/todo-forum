# tests/test_threads.py

import pytest
from tests.factories import create_user, create_thread


@pytest.mark.asyncio
async def test_create_and_get_thread(async_client, db_session):
    user = create_user(db_session, username="u1")

    # login
    res = await async_client.post("/auth/token", json={"username": "u1", "password": "pass123"})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # create thread
    payload = {"title": "t1", "content": "c1"}
    res2 = await async_client.post("/threads/", json=payload, headers=headers)
    assert res2.status_code == 201
    thread_id = res2.json()["id"]

    # get thread
    res3 = await async_client.get(f"/threads/{thread_id}")
    assert res3.status_code == 200
    assert res3.json()["id"] == thread_id


@pytest.mark.asyncio
async def test_update_thread_forbidden(async_client, db_session):
    owner = create_user(db_session, username="owner")
    other = create_user(db_session, username="hacker")
    thread = create_thread(db_session, owner_id=owner.id)

    # login as other
    res = await async_client.post("/auth/token", json={
        "username": "hacker",
        "password": "pass123"
    })
    token = res.json()["access_token"]

    # try to update
    res2 = await async_client.put(
        f"/threads/{thread.id}",
        json={"title": "x", "content": "y"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res2.status_code == 403
