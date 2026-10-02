"""Participants API Router (S1-T3, TAD §8, §27)."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from packages.contracts.auth import AuthUser
from packages.contracts.entities import ParticipantCreate, ParticipantRead, ParticipantUpdate
from packages.contracts.envelope import ResponseEnvelope, make_success_envelope
from packages.domain.database import get_db_session
from packages.domain.models import Participant
from packages.domain.repository import DomainRepository, EntityNotFoundError, StaleRevisionError
from services.api.auth.dependencies import get_current_user
from services.api.auth.rbac import Permission, check_event_scope, require_permission
from services.api.idempotency import get_idempotency_store

router = APIRouter(prefix="/api/v1/participants", tags=["participants"])


@router.get(
    "",
    response_model=ResponseEnvelope[list[ParticipantRead]],
    summary="List participants",
    dependencies=[Depends(require_permission(Permission.VENUE_READ))],
)
async def list_participants(
    request: Request,
    event_id: str | None = None,
    role: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[list[ParticipantRead]]:
    target_event = event_id or user.event_id
    if target_event and not check_event_scope(user, target_event):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Event scope mismatch (BR-018)")

    repo = DomainRepository(Participant, db)
    offset = (page - 1) * limit
    filters = {"role": role} if role else None
    participants, total = await repo.list_entities(event_id=target_event, offset=offset, limit=limit, filters=filters)
    items = [ParticipantRead.model_validate(p) for p in participants]
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
    response_model=ResponseEnvelope[ParticipantRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create participant",
    dependencies=[Depends(require_permission(Permission.VOLUNTEER_WRITE))],
)
async def create_participant(
    request: Request,
    body: ParticipantCreate,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    db: AsyncSession = Depends(get_db_session),
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[ParticipantRead]:
    if not check_event_scope(user, body.event_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Event scope mismatch (BR-018)")

    store = get_idempotency_store()
    if idempotency_key:
        cached = store.get(idempotency_key)
        if cached:
            return ResponseEnvelope[ParticipantRead].model_validate(cached[1])

    repo = DomainRepository(Participant, db)
    existing = await repo.get_by_id(body.participant_id, event_id=body.event_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Participant {body.participant_id} already exists")

    participant = Participant(
        participant_id=body.participant_id,
        event_id=body.event_id,
        name=body.name,
        email=body.email,
        role=body.role.value,
        arrival_building=body.arrival_building,
        assigned_session_id=body.assigned_session_id,
        assigned_venue_id=body.assigned_venue_id,
        skill=body.skill,
        volunteer_status=body.volunteer_status.value if body.volunteer_status else None,
        metadata_json=body.metadata_json,
    )
    created = await repo.create(
        participant,
        actor_id=user.user_id,
        event_id=body.event_id,
        correlation_id=request.headers.get("X-Correlation-ID"),
    )
    result = ParticipantRead.model_validate(created)
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
    "/{participant_id}",
    response_model=ResponseEnvelope[ParticipantRead],
    summary="Get participant by ID",
    dependencies=[Depends(require_permission(Permission.VENUE_READ))],
)
async def get_participant(
    participant_id: str,
    request: Request,
    event_id: str | None = None,
    db: AsyncSession = Depends(get_db_session),
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[ParticipantRead]:
    target_event = event_id or user.event_id
    repo = DomainRepository(Participant, db)
    participant = await repo.get_by_id(participant_id, event_id=target_event)
    if not participant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Participant {participant_id} not found")

    if not check_event_scope(user, participant.event_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Event scope mismatch (BR-018)")

    return make_success_envelope(
        ParticipantRead.model_validate(participant),
        request_id=str(uuid.uuid4()),
        correlation_id=request.headers.get("X-Correlation-ID"),
        revision=participant.revision,
    )


@router.put(
    "/{participant_id}",
    response_model=ResponseEnvelope[ParticipantRead],
    summary="Update participant with optimistic concurrency",
    dependencies=[Depends(require_permission(Permission.VOLUNTEER_WRITE))],
)
async def update_participant(
    participant_id: str,
    request: Request,
    body: ParticipantUpdate,
    if_match: Annotated[str | None, Header(alias="If-Match")] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    event_id: str | None = None,
    db: AsyncSession = Depends(get_db_session),
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[ParticipantRead]:
    target_event = event_id or user.event_id or "evt_kbc2026"
    if not check_event_scope(user, target_event):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Event scope mismatch (BR-018)")

    store = get_idempotency_store()
    if idempotency_key:
        cached = store.get(idempotency_key)
        if cached:
            return ResponseEnvelope[ParticipantRead].model_validate(cached[1])

    expected_rev = int(if_match) if if_match and if_match.isdigit() else None
    repo = DomainRepository(Participant, db)
    updates = body.model_dump(exclude_unset=True)
    if "role" in updates and updates["role"] is not None:
        updates["role"] = updates["role"].value
    if "volunteer_status" in updates and updates["volunteer_status"] is not None:
        updates["volunteer_status"] = updates["volunteer_status"].value

    try:
        updated = await repo.update(
            participant_id,
            updates,
            expected_revision=expected_rev,
            actor_id=user.user_id,
            event_id=target_event,
            correlation_id=request.headers.get("X-Correlation-ID"),
        )
    except StaleRevisionError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    result = ParticipantRead.model_validate(updated)
    response_data = make_success_envelope(
        result,
        request_id=str(uuid.uuid4()),
        correlation_id=request.headers.get("X-Correlation-ID"),
        revision=updated.revision,
    )
    if idempotency_key:
        store.set(idempotency_key, 200, response_data.model_dump(mode="json"))
    return response_data
