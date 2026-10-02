"""Venues API Router (S1-T3, TAD §8, §27)."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from packages.contracts.auth import AuthUser
from packages.contracts.entities import VenueCreate, VenueRead, VenueUpdate
from packages.contracts.envelope import ResponseEnvelope, make_success_envelope
from packages.domain.database import get_db_session
from packages.domain.models import Venue
from packages.domain.repository import DomainRepository, EntityNotFoundError, StaleRevisionError
from services.api.auth.dependencies import get_current_user
from services.api.auth.rbac import Permission, check_event_scope, require_permission
from services.api.idempotency import get_idempotency_store

router = APIRouter(prefix="/api/v1/venues", tags=["venues"])


@router.get(
    "",
    response_model=ResponseEnvelope[list[VenueRead]],
    summary="List venues",
    dependencies=[Depends(require_permission(Permission.VENUE_READ))],
)
async def list_venues(
    request: Request,
    event_id: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[list[VenueRead]]:
    target_event = event_id or user.event_id
    if target_event and not check_event_scope(user, target_event):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Event scope mismatch (BR-018)")

    repo = DomainRepository(Venue, db)
    offset = (page - 1) * limit
    venues, total = await repo.list_entities(event_id=target_event, offset=offset, limit=limit)
    items = [VenueRead.model_validate(v) for v in venues]
    return make_success_envelope(
        items,
        request_id=str(uuid.uuid4()),
        correlation_id=request.headers.get("X-Correlation-ID"),
        page=page,
        limit=limit,
        total=total,
    )


@router.post(
    "",
    response_model=ResponseEnvelope[VenueRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create venue",
    dependencies=[Depends(require_permission(Permission.VENUE_WRITE))],
)
async def create_venue(
    request: Request,
    body: VenueCreate,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    db: AsyncSession = Depends(get_db_session),
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[VenueRead]:
    if not check_event_scope(user, body.event_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Event scope mismatch (BR-018)")

    store = get_idempotency_store()
    if idempotency_key:
        cached = store.get(idempotency_key)
        if cached:
            return ResponseEnvelope[VenueRead].model_validate(cached[1])

    repo = DomainRepository(Venue, db)
    existing = await repo.get_by_id(body.venue_id, event_id=body.event_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Venue {body.venue_id} already exists")

    venue = Venue(
        venue_id=body.venue_id,
        event_id=body.event_id,
        name=body.name,
        capacity=body.capacity,
        building=body.building,
        venue_type=body.venue_type.value,
        is_available=body.is_available,
        metadata_json=body.metadata_json,
    )
    created = await repo.create(
        venue,
        actor_id=user.user_id,
        event_id=body.event_id,
        correlation_id=request.headers.get("X-Correlation-ID"),
    )
    result = VenueRead.model_validate(created)
    response_data = make_success_envelope(
        result,
        request_id=str(uuid.uuid4()),
        correlation_id=request.headers.get("X-Correlation-ID"),
        revision=created.revision,
    )
    if idempotency_key:
        store.set(idempotency_key, 201, response_data.model_dump(mode="json"))
    return response_data


@router.get(
    "/{venue_id}",
    response_model=ResponseEnvelope[VenueRead],
    summary="Get venue by ID",
    dependencies=[Depends(require_permission(Permission.VENUE_READ))],
)
async def get_venue(
    venue_id: str,
    request: Request,
    event_id: str | None = None,
    db: AsyncSession = Depends(get_db_session),
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[VenueRead]:
    target_event = event_id or user.event_id
    repo = DomainRepository(Venue, db)
    venue = await repo.get_by_id(venue_id, event_id=target_event)
    if not venue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Venue {venue_id} not found")

    if not check_event_scope(user, venue.event_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Event scope mismatch (BR-018)")

    return make_success_envelope(
        VenueRead.model_validate(venue),
        request_id=str(uuid.uuid4()),
        correlation_id=request.headers.get("X-Correlation-ID"),
        revision=venue.revision,
    )


@router.put(
    "/{venue_id}",
    response_model=ResponseEnvelope[VenueRead],
    summary="Update venue with optimistic concurrency",
    dependencies=[Depends(require_permission(Permission.VENUE_WRITE))],
)
async def update_venue(
    venue_id: str,
    request: Request,
    body: VenueUpdate,
    if_match: Annotated[str | None, Header(alias="If-Match")] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    event_id: str | None = None,
    db: AsyncSession = Depends(get_db_session),
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[VenueRead]:
    target_event = event_id or user.event_id or "evt_kbc2026"
    if not check_event_scope(user, target_event):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Event scope mismatch (BR-018)")

    store = get_idempotency_store()
    if idempotency_key:
        cached = store.get(idempotency_key)
        if cached:
            return ResponseEnvelope[VenueRead].model_validate(cached[1])

    expected_rev = int(if_match) if if_match and if_match.isdigit() else None
    repo = DomainRepository(Venue, db)
    try:
        updated = await repo.update(
            venue_id,
            body.model_dump(exclude_unset=True),
            expected_revision=expected_rev,
            actor_id=user.user_id,
            event_id=target_event,
            correlation_id=request.headers.get("X-Correlation-ID"),
        )
    except StaleRevisionError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    result = VenueRead.model_validate(updated)
    response_data = make_success_envelope(
        result,
        request_id=str(uuid.uuid4()),
        correlation_id=request.headers.get("X-Correlation-ID"),
        revision=updated.revision,
    )
    if idempotency_key:
        store.set(idempotency_key, 200, response_data.model_dump(mode="json"))
    return response_data
