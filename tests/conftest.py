"""Root conftest for KoreX test suite.

Shared fixtures available to all test modules.
"""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from packages.domain.database import get_db_session
from packages.domain.models import Base
from services.api.auth.providers import DevLoginProvider
from services.api.main import app

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(autouse=True)
def app_env() -> AsyncGenerator[str, None]:
    """Ensure tests run with APP_ENV=development."""
    original = os.environ.get("APP_ENV")
    os.environ["APP_ENV"] = "development"
    yield "development"
    if original is None:
        os.environ.pop("APP_ENV", None)
    else:
        os.environ["APP_ENV"] = original


@pytest.fixture()
async def test_engine():
    """Create in-memory SQLite async engine."""
    engine = create_async_engine(
        TEST_DB_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture()
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide clean database session for each test."""
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    async with session_factory() as session:
        yield session


@pytest.fixture()
async def async_client(test_engine, db_session) -> AsyncGenerator[AsyncClient, None]:
    """Provide AsyncClient with DB session override."""
    async def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db_session] = _get_test_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers() -> dict[str, str]:
    """Provide bearer auth header for super_admin."""
    provider = DevLoginProvider()
    token = provider.create_token(
        email="admin@korex.kiit.ac.in",
        name="Super Admin",
        roles=["super_admin"],
        event_id="evt_kbc2026",
    )
    return {"Authorization": f"Bearer {token}"}
