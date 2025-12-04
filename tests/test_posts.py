# tests/test_posts.py

import pytest
from tests.factories import create_user, create_thread
from app.models.notification import Notification


@pytest.mark.asyncio
async def test_create_post_and_notify(async_client, db_session):
    owner = create_user(db_session, username="owner")
    poster = create_user(db_session, username="poster")
    thread = create_thread(db_session, owner_id=owner.id)

    # login as poster
    res = await async_client.post("/auth/token", json={"username": "poster", "password": "pass123"})
    token = res.json()["access_token"]

    payload = {"content": "hello"}
    res2 = await async_client.post(
        f"/threads/{thread.id}/posts",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res2.status_code == 200

    # verify notification
    note = db_session.query(Notification).filter_by(user_id=owner.id).first()
    assert note is not None
