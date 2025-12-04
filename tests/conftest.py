# tests/conftest.py
"""
Session/DB fixtures and AsyncClient for tests.
Session strategy:
- Create tables once per test session
- Each test runs inside a transaction and rolls back afterward
"""

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient
from starlette.testclient import TestClient

from app.main import app
from app.db.base import Base
from app.db.session import engine as project_engine, SessionLocal as ProjectSessionLocal, get_db
from app.utils.security import create_access_token
from app.core.config import settings
import pytest_asyncio
from httpx import AsyncClient,ASGITransport

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", settings.DATABASE_URL)

engine = project_engine
SessionLocal = ProjectSessionLocal


import app.db.session as session_module

@pytest.fixture(autouse=True)
def override_sessionlocal(db_session):
    session_module.SessionLocal = lambda: db_session


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    connection = engine.connect()
    transaction = connection.begin()

    session = SessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(autouse=True)
def override_get_db(db_session):
    def _override():
        yield db_session

    app.dependency_overrides[get_db] = _override


import pytest_asyncio
from httpx import AsyncClient, ASGITransport

@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def create_token_for_user():
    def _create(user_id: int, expires_delta=None):
        return create_access_token(str(user_id), expires_delta)
    return _create
