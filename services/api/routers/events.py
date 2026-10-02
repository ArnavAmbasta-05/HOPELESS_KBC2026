"""Events API Router (S1-T3, TAD §8, §27)."""

from __future__ import annotations

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from packages.contracts.auth import AuthUser
from packages.contracts.entities import EventCreate, EventRead, EventUpdate
from packages.contracts.envelope import ResponseEnvelope, make_error_envelope, make_success_envelope
from packages.domain.database import get_db_session
from packages.domain.models import Event
from packages.domain.repository import DomainRepository, EntityNotFoundError, StaleRevisionError
from services.api.auth.dependencies import get_current_user
from services.api.auth.rbac import Permission, require_permission
from services.api.idempotency import get_idempotency_store

router = APIRouter(prefix="/api/v1/events", tags=["events"])


@router.get(
    "",
    response_model=ResponseEnvelope[list[EventRead]],
    summary="List events",
    dependencies=[Depends(require_permission(Permission.VENUE_READ))],
)
async def list_events(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[list[EventRead]]:
    repo = DomainRepository(Event, db)
    offset = (page - 1) * limit
    events, total = await repo.list_entities(offset=offset, limit=limit)
    items = [EventRead.model_validate(e) for e in events]
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
    response_model=ResponseEnvelope[EventRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create event",
    dependencies=[Depends(require_permission(Permission.ADMIN_MANAGE))],
)
async def create_event(
    request: Request,
    body: EventCreate,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    db: AsyncSession = Depends(get_db_session),
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[EventRead]:
    store = get_idempotency_store()
    if idempotency_key:
        cached = store.get(idempotency_key)
        if cached:
            return ResponseEnvelope[EventRead].model_validate(cached[1])

    repo = DomainRepository(Event, db)
    existing = await repo.get_by_id(body.event_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Event {body.event_id} already exists",
        )

    event = Event(
        event_id=body.event_id,
        name=body.name,
        description=body.description,
        start_date=body.start_date,
        end_date=body.end_date,
        timezone=body.timezone,
        metadata_json=body.metadata_json,
    )
    created = await repo.create(
        event,
        actor_id=user.user_id,
        event_id=body.event_id,
        correlation_id=request.headers.get("X-Correlation-ID"),
    )
    result = EventRead.model_validate(created)
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
    "/{event_id}",
    response_model=ResponseEnvelope[EventRead],
    summary="Get event by ID",
    dependencies=[Depends(require_permission(Permission.VENUE_READ))],
)
async def get_event(
    event_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[EventRead]:
    repo = DomainRepository(Event, db)
    event = await repo.get_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event {event_id} not found",
        )
    return make_success_envelope(
        EventRead.model_validate(event),
        request_id=str(uuid.uuid4()),
        correlation_id=request.headers.get("X-Correlation-ID"),
        revision=event.revision,
    )


@router.put(
    "/{event_id}",
    response_model=ResponseEnvelope[EventRead],
    summary="Update event with optimistic concurrency",
    dependencies=[Depends(require_permission(Permission.ADMIN_MANAGE))],
)
async def update_event(
    event_id: str,
    request: Request,
    body: EventUpdate,
    if_match: Annotated[str | None, Header(alias="If-Match")] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    db: AsyncSession = Depends(get_db_session),
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[EventRead]:
    store = get_idempotency_store()
    if idempotency_key:
        cached = store.get(idempotency_key)
        if cached:
            return ResponseEnvelope[EventRead].model_validate(cached[1])

    expected_rev = int(if_match) if if_match and if_match.isdigit() else None
    repo = DomainRepository(Event, db)
    try:
        updated = await repo.update(
            event_id,
            body.model_dump(exclude_unset=True),
            expected_revision=expected_rev,
            actor_id=user.user_id,
            event_id=event_id,
            correlation_id=request.headers.get("X-Correlation-ID"),
        )
    except StaleRevisionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except EntityNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    result = EventRead.model_validate(updated)
    response_data = make_success_envelope(
        result,
        request_id=str(uuid.uuid4()),
        correlation_id=request.headers.get("X-Correlation-ID"),
        revision=updated.revision,
    )
    if idempotency_key:
        store.set(idempotency_key, 200, response_data.model_dump(mode="json"))
    return response_data
