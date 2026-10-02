"""SQLAlchemy declarative base and common mixins for KoreX domain entities.

Provides:
- Base: DeclarativeBase for all models
- TimestampMixin: created_at, updated_at with UTC defaults
- RevisionMixin: revision integer for optimistic concurrency (TAD §18.2)
- TenantScopedMixin: event_id for multi-event tenant isolation (BR-018)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, Integer, String, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now() -> datetime:
    """Return timezone-aware current UTC datetime."""
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Declarative base class for all SQLAlchemy domain models."""
    pass


class TimestampMixin:
    """Provides created_at and updated_at timestamps in UTC."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )


class RevisionMixin:
    """Provides revision tracking for optimistic concurrency (TAD §18.2, AT-06)."""

    revision: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )


class TenantScopedMixin:
    """Provides event_id for multi-event tenant isolation (BR-018)."""

    event_id: Mapped[str] = mapped_column(
        String(64),
        index=True,
        nullable=False,
    )
