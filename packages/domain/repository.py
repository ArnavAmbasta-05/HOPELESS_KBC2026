"""Domain repository layer for KoreX (S1-T2, S1-T4).

Implements:
1. Event-level multi-tenant isolation (BR-018)
2. Optimistic concurrency with revision checks (TAD §18.2, AT-06)
3. Append-only audit logging hook for every mutation (BR-015, S1-T4)
"""

from __future__ import annotations

import uuid
from typing import Any, Generic, Sequence, TypeVar

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from packages.domain.models import AuditRecord, Base

T = TypeVar("T", bound=Base)


class StaleRevisionError(Exception):
    """Raised when an update contains a stale If-Match revision (AT-06 primitive)."""

    def __init__(self, expected_revision: int, current_revision: int) -> None:
        super().__init__(
            f"Stale revision conflict: expected revision {expected_revision}, "
            f"but current revision is {current_revision}"
        )
        self.expected_revision = expected_revision
        self.current_revision = current_revision


class EntityNotFoundError(Exception):
    """Raised when requested entity is not found within the event scope."""
    pass


def _serialize_state(entity: T) -> dict[str, Any]:
    """Serialize entity columns to JSON-compatible dict."""
    state: dict[str, Any] = {}
    for c in entity.__table__.columns:
        if c.name == "metadata_json":
            continue
        val = getattr(entity, c.name, None)
        if hasattr(val, "isoformat"):
            state[c.name] = val.isoformat()
        else:
            state[c.name] = val
    return state


class DomainRepository(Generic[T]):
    """Generic repository with tenant-isolation, optimistic concurrency, and audit logging."""

    def __init__(self, model_class: type[T], session: AsyncSession) -> None:
        self.model_class = model_class
        self.session = session

    async def get_by_id(
        self,
        entity_id: str,
        *,
        event_id: str | None = None,
    ) -> T | None:
        """Fetch an entity by primary key with optional event tenant check."""
        pk_column = list(self.model_class.__table__.primary_key.columns)[0]
        query = select(self.model_class).where(pk_column == entity_id)

        if event_id is not None and hasattr(self.model_class, "event_id"):
            query = query.where(getattr(self.model_class, "event_id") == event_id)

        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_entities(
        self,
        *,
        event_id: str | None = None,
        offset: int = 0,
        limit: int = 50,
        filters: dict[str, Any] | None = None,
    ) -> tuple[Sequence[T], int]:
        """List entities with filtering, tenant isolation, and total count."""
        query = select(self.model_class)
        count_query = select(func.count()).select_from(self.model_class)

        if event_id is not None and hasattr(self.model_class, "event_id"):
            query = query.where(getattr(self.model_class, "event_id") == event_id)
            count_query = count_query.where(getattr(self.model_class, "event_id") == event_id)

        if filters:
            for key, val in filters.items():
                if hasattr(self.model_class, key) and val is not None:
                    query = query.where(getattr(self.model_class, key) == val)
                    count_query = count_query.where(getattr(self.model_class, key) == val)

        total_res = await self.session.execute(count_query)
        total = total_res.scalar() or 0

        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all(), total

    async def create(
        self,
        entity: T,
        *,
        actor_id: str,
        event_id: str,
        trace_id: str | None = None,
        correlation_id: str | None = None,
    ) -> T:
        """Persist a new entity and write an append-only audit record."""
        self.session.add(entity)
        await self.session.flush()

        pk_column = list(self.model_class.__table__.primary_key.columns)[0]
        entity_id = str(getattr(entity, pk_column.name))

        # Record audit log
        after_state = _serialize_state(entity)
        audit = AuditRecord(
            audit_id=f"aud_{uuid.uuid4().hex[:12]}",
            event_id=event_id,
            actor_id=actor_id,
            action=f"{self.model_class.__tablename__}.create",
            entity_type=self.model_class.__tablename__,
            entity_id=entity_id,
            before_state=None,
            after_state=after_state,
            trace_id=trace_id,
            correlation_id=correlation_id,
        )
        self.session.add(audit)
        await self.session.flush()
        return entity

    async def update(
        self,
        entity_id: str,
        updates: dict[str, Any],
        *,
        expected_revision: int | None = None,
        actor_id: str,
        event_id: str,
        trace_id: str | None = None,
        correlation_id: str | None = None,
    ) -> T:
        """Update an entity with optimistic concurrency checking and audit log."""
        entity = await self.get_by_id(entity_id, event_id=event_id)
        if entity is None:
            raise EntityNotFoundError(f"{self.model_class.__name__} {entity_id} not found in event {event_id}")

        before_state = _serialize_state(entity)

        # Optimistic concurrency check (AT-06)
        if hasattr(entity, "revision"):
            current_rev = getattr(entity, "revision")
            if expected_revision is not None and expected_revision != current_rev:
                raise StaleRevisionError(expected_revision=expected_revision, current_revision=current_rev)

            # Bump revision on write (TAD §18.2)
            setattr(entity, "revision", current_rev + 1)

        # Apply updates
        for key, val in updates.items():
            if hasattr(entity, key) and val is not None:
                setattr(entity, key, val)

        await self.session.flush()

        after_state = _serialize_state(entity)

        # Write audit record
        audit = AuditRecord(
            audit_id=f"aud_{uuid.uuid4().hex[:12]}",
            event_id=event_id,
            actor_id=actor_id,
            action=f"{self.model_class.__tablename__}.update",
            entity_type=self.model_class.__tablename__,
            entity_id=entity_id,
            before_state=before_state,
            after_state=after_state,
            trace_id=trace_id,
            correlation_id=correlation_id,
        )
        self.session.add(audit)
        await self.session.flush()
        return entity
