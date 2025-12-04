# tests/test_comments.py

import pytest
from tests.factories import create_user, create_thread, create_post


@pytest.mark.asyncio
async def test_create_comment_and_tree(async_client, db_session):
    owner = create_user(db_session, username="owner_c")
    commenter = create_user(db_session, username="commenter")
    thread = create_thread(db_session, owner_id=owner.id)
    post = create_post(db_session, thread_id=thread.id, user_id=owner.id)

    # login commenter
    res = await async_client.post("/auth/token", json={
        "username": commenter.username,
        "password": "pass123"
    })
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # root comment
    res2 = await async_client.post(
        f"/posts/{post.id}/comments/",
        json={"content": "root"},
        headers=headers
    )
    assert res2.status_code == 200
    root_id = res2.json()["id"]

    # reply
    res3 = await async_client.post(
        f"/posts/{post.id}/comments/",
        json={"content": "reply", "parent_id": root_id},
        headers=headers
    )
    assert res3.status_code == 200

    # tree
    res4 = await async_client.get(f"/posts/{post.id}/comments/tree")
    assert res4.status_code == 200
    assert isinstance(res4.json(), list)
