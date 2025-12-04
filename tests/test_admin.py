# tests/test_admin.py

import pytest
from tests.factories import create_admin, create_user, create_thread


@pytest.mark.asyncio
async def test_admin_promote_demote(async_client, db_session):
    admin = create_admin(db_session, username="superadmin")
    user = create_user(db_session, username="normaluser")

    # login as admin
    res = await async_client.post("/auth/token", json={
        "username": "superadmin",
        "password": "adminpass"
    })
    token = res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # promote
    r2 = await async_client.put(f"/admin/users/{user.id}/promote", headers=headers)
    assert r2.status_code == 200
    assert "promoted" in r2.json()["message"]

    # demote
    r3 = await async_client.put(f"/admin/users/{user.id}/demote", headers=headers)
    assert r3.status_code == 200
    assert "demoted" in r3.json()["message"]


@pytest.mark.asyncio
async def test_admin_delete_thread(async_client, db_session):
    admin = create_admin(db_session, username="super2")
    user = create_user(db_session, username="ownerthread")
    thread = create_thread(db_session, owner_id=user.id)

    # login as admin
    res = await async_client.post("/auth/token", json={
        "username": "super2",
        "password": "adminpass"
    })
    token = res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    res2 = await async_client.delete(f"/admin/threads/{thread.id}", headers=headers)
    assert res2.status_code == 200
    assert "deleted" in res2.json()["message"]
