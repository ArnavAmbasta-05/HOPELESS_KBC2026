"""Sessions API Router (S1-T3, TAD §8, §27)."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from packages.contracts.auth import AuthUser
from packages.contracts.entities import SessionCreate, SessionRead, SessionUpdate
from packages.contracts.envelope import ResponseEnvelope, make_success_envelope
from packages.domain.database import get_db_session
from packages.domain.models import Session as SessionModel
from packages.domain.repository import DomainRepository, EntityNotFoundError, StaleRevisionError
from services.api.auth.dependencies import get_current_user
from services.api.auth.rbac import Permission, check_event_scope, require_permission
from services.api.idempotency import get_idempotency_store

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


@router.get(
    "",
    response_model=ResponseEnvelope[list[SessionRead]],
    summary="List sessions",
    dependencies=[Depends(require_permission(Permission.SESSION_READ))],
)
async def list_sessions(
    request: Request,
    event_id: str | None = None,
    venue_id: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[list[SessionRead]]:
    target_event = event_id or user.event_id
    if target_event and not check_event_scope(user, target_event):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Event scope mismatch (BR-018)")

    repo = DomainRepository(SessionModel, db)
    offset = (page - 1) * limit
    filters = {"venue_id": venue_id} if venue_id else None
    sessions, total = await repo.list_entities(event_id=target_event, offset=offset, limit=limit, filters=filters)
    items = [SessionRead.model_validate(s) for s in sessions]
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
    response_model=ResponseEnvelope[SessionRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create session",
    dependencies=[Depends(require_permission(Permission.SESSION_WRITE))],
)
async def create_session(
    request: Request,
    body: SessionCreate,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    db: AsyncSession = Depends(get_db_session),
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[SessionRead]:
    if not check_event_scope(user, body.event_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Event scope mismatch (BR-018)")

    store = get_idempotency_store()
    if idempotency_key:
        cached = store.get(idempotency_key)
        if cached:
            return ResponseEnvelope[SessionRead].model_validate(cached[1])

    repo = DomainRepository(SessionModel, db)
    existing = await repo.get_by_id(body.session_id, event_id=body.event_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Session {body.session_id} already exists")

    session_obj = SessionModel(
        session_id=body.session_id,
        event_id=body.event_id,
        name=body.name,
        description=body.description,
        venue_id=body.venue_id,
        session_date=body.session_date,
        start_time=body.start_time,
        end_time=body.end_time,
        registrants=body.registrants,
        status=body.status.value,
        metadata_json=body.metadata_json,
    )
    created = await repo.create(
        session_obj,
        actor_id=user.user_id,
        event_id=body.event_id,
        correlation_id=request.headers.get("X-Correlation-ID"),
    )
    result = SessionRead.model_validate(created)
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
    "/{session_id}",
    response_model=ResponseEnvelope[SessionRead],
    summary="Get session by ID",
    dependencies=[Depends(require_permission(Permission.SESSION_READ))],
)
async def get_session(
    session_id: str,
    request: Request,
    event_id: str | None = None,
    db: AsyncSession = Depends(get_db_session),
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[SessionRead]:
    target_event = event_id or user.event_id
    repo = DomainRepository(SessionModel, db)
    session_obj = await repo.get_by_id(session_id, event_id=target_event)
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {session_id} not found")

    if not check_event_scope(user, session_obj.event_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Event scope mismatch (BR-018)")

    return make_success_envelope(
        SessionRead.model_validate(session_obj),
        request_id=str(uuid.uuid4()),
        correlation_id=request.headers.get("X-Correlation-ID"),
        revision=session_obj.revision,
    )


@router.put(
    "/{session_id}",
    response_model=ResponseEnvelope[SessionRead],
    summary="Update session with optimistic concurrency",
    dependencies=[Depends(require_permission(Permission.SESSION_WRITE))],
)
async def update_session(
    session_id: str,
    request: Request,
    body: SessionUpdate,
    if_match: Annotated[str | None, Header(alias="If-Match")] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    event_id: str | None = None,
    db: AsyncSession = Depends(get_db_session),
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[SessionRead]:
    target_event = event_id or user.event_id or "evt_kbc2026"
    if not check_event_scope(user, target_event):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Event scope mismatch (BR-018)")

    store = get_idempotency_store()
    if idempotency_key:
        cached = store.get(idempotency_key)
        if cached:
            return ResponseEnvelope[SessionRead].model_validate(cached[1])

    expected_rev = int(if_match) if if_match and if_match.isdigit() else None
    repo = DomainRepository(SessionModel, db)
    updates = body.model_dump(exclude_unset=True)
    if "status" in updates and updates["status"] is not None:
        updates["status"] = updates["status"].value

    try:
        updated = await repo.update(
            session_id,
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

    result = SessionRead.model_validate(updated)
    response_data = make_success_envelope(
        result,
        request_id=str(uuid.uuid4()),
        correlation_id=request.headers.get("X-Correlation-ID"),
        revision=updated.revision,
    )
    if idempotency_key:
        store.set(idempotency_key, 200, response_data.model_dump(mode="json"))
    return response_data
