"""Database connection and session management for KoreX (SQLAlchemy 2 Async)."""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Default to asyncpg url or SQLite in-memory for unit testing if not set
DEFAULT_DATABASE_URL = "postgresql+asyncpg://korex:changeme@localhost:5432/korex"


def get_database_url() -> str:
    """Retrieve database URL from environment or return default."""
    url = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
    # Ensure async driver for sqlite if used in tests
    if url.startswith("sqlite://") and not url.startswith("sqlite+aiosqlite://"):
        url = url.replace("sqlite://", "sqlite+aiosqlite://")
    return url


_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Return singleton AsyncEngine."""
    global _engine  # noqa: PLW0603
    if _engine is None:
        db_url = get_database_url()
        kwargs: dict[str, object] = {"echo": False, "future": True}
        if "sqlite" in db_url:
            kwargs["connect_args"] = {"check_same_thread": False}
        _engine = create_async_engine(db_url, **kwargs)
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return singleton async session factory."""
    global _session_factory  # noqa: PLW0603
    if _session_factory is None:
        engine = get_engine()
        _session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for obtaining an asynchronous DB session."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
