# tests/test_auth.py

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login(async_client, db_session):
    # Register
    payload = {
        "username": "tester",
        "email": "tester@example.com",
        "password": "pass123"
    }
    res = await async_client.post("/auth/register", json=payload)
    assert res.status_code == 201
    assert res.json()["username"] == "tester"

    # Login
    login = {"username": "tester", "password": "pass123"}
    res2 = await async_client.post("/auth/token", json=login)
    assert res2.status_code == 200
    assert "access_token" in res2.json()


@pytest.mark.asyncio
async def test_login_failure(async_client):
    res = await async_client.post("/auth/token", json={
        "username": "wrong",
        "password": "wrong"
    })
    assert res.status_code == 401
