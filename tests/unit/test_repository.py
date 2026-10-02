"""Unit tests for repository optimistic concurrency, tenant isolation, and audit logging (S1-T2, S1-T4)."""

from __future__ import annotations

import datetime as dt
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from packages.domain.models import AuditRecord, Venue
from packages.domain.repository import DomainRepository, EntityNotFoundError, StaleRevisionError


@pytest.mark.asyncio
async def test_repository_crud_and_revision_bumping(db_session: AsyncSession) -> None:
    repo = DomainRepository(Venue, db_session)
    venue = Venue(
        venue_id="ven_repo_1",
        event_id="evt_kbc2026",
        name="Main Hall",
        capacity=500,
        building="Bldg A",
        venue_type="indoor",
    )
    created = await repo.create(
        venue,
        actor_id="user_admin",
        event_id="evt_kbc2026",
    )
    assert created.revision == 1

    # Update with correct revision
    updated = await repo.update(
        "ven_repo_1",
        {"capacity": 550},
        expected_revision=1,
        actor_id="user_admin",
        event_id="evt_kbc2026",
    )
    assert updated.capacity == 550
    assert updated.revision == 2


@pytest.mark.asyncio
async def test_stale_revision_raises_error(db_session: AsyncSession) -> None:
    repo = DomainRepository(Venue, db_session)
    venue = Venue(
        venue_id="ven_repo_conflict",
        event_id="evt_kbc2026",
        name="Conflict Hall",
        capacity=200,
        building="Bldg B",
        venue_type="indoor",
    )
    await repo.create(venue, actor_id="user_admin", event_id="evt_kbc2026")

    # Pass stale revision (e.g. 99 instead of 1)
    with pytest.raises(StaleRevisionError) as exc_info:
        await repo.update(
            "ven_repo_conflict",
            {"capacity": 250},
            expected_revision=99,
            actor_id="user_admin",
            event_id="evt_kbc2026",
        )
    assert exc_info.value.expected_revision == 99
    assert exc_info.value.current_revision == 1


@pytest.mark.asyncio
async def test_tenant_event_isolation(db_session: AsyncSession) -> None:
    repo = DomainRepository(Venue, db_session)
    venue_a = Venue(
        venue_id="ven_iso_a",
        event_id="evt_alpha",
        name="Alpha Hall",
        capacity=100,
        building="Bldg A",
        venue_type="indoor",
    )
    await repo.create(venue_a, actor_id="user_admin", event_id="evt_alpha")

    # Querying with different event_id returns None (BR-018)
    found_in_beta = await repo.get_by_id("ven_iso_a", event_id="evt_beta")
    assert found_in_beta is None

    # Querying with correct event_id returns entity
    found_in_alpha = await repo.get_by_id("ven_iso_a", event_id="evt_alpha")
    assert found_in_alpha is not None


@pytest.mark.asyncio
async def test_audit_record_emitted_on_mutations(db_session: AsyncSession) -> None:
    venue_repo = DomainRepository(Venue, db_session)
    audit_repo = DomainRepository(AuditRecord, db_session)

    venue = Venue(
        venue_id="ven_audit_test",
        event_id="evt_kbc2026",
        name="Audited Hall",
        capacity=400,
        building="Bldg C",
        venue_type="indoor",
    )
    await venue_repo.create(venue, actor_id="user_actor_1", event_id="evt_kbc2026")
    await venue_repo.update(
        "ven_audit_test",
        {"capacity": 420},
        actor_id="user_actor_2",
        event_id="evt_kbc2026",
    )

    logs, total = await audit_repo.list_entities(
        event_id="evt_kbc2026",
        filters={"entity_id": "ven_audit_test"},
    )
    assert total == 2
    actions = [log.action for log in logs]
    assert "venues.create" in actions
    assert "venues.update" in actions
