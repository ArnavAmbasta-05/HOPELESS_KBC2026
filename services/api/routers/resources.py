"""Resources API Router (S1-T3, TAD §8, §27)."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from packages.contracts.auth import AuthUser
from packages.contracts.entities import ResourceCreate, ResourceRead, ResourceUpdate
from packages.contracts.envelope import ResponseEnvelope, make_success_envelope
from packages.domain.database import get_db_session
from packages.domain.models import Resource
from packages.domain.repository import DomainRepository, EntityNotFoundError, StaleRevisionError
from services.api.auth.dependencies import get_current_user
from services.api.auth.rbac import Permission, check_event_scope, require_permission
from services.api.idempotency import get_idempotency_store

router = APIRouter(prefix="/api/v1/resources", tags=["resources"])


@router.get(
    "",
    response_model=ResponseEnvelope[list[ResourceRead]],
    summary="List resources",
    dependencies=[Depends(require_permission(Permission.VENUE_READ))],
)
async def list_resources(
    request: Request,
    event_id: str | None = None,
    category: str | None = None,
    location: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[list[ResourceRead]]:
    target_event = event_id or user.event_id
    if target_event and not check_event_scope(user, target_event):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Event scope mismatch (BR-018)")

    repo = DomainRepository(Resource, db)
    offset = (page - 1) * limit
    filters: dict[str, str] = {}
    if category:
        filters["category"] = category
    if location:
        filters["location"] = location

    resources, total = await repo.list_entities(
        event_id=target_event,
        offset=offset,
        limit=limit,
        filters=filters if filters else None,
    )
    items = [ResourceRead.model_validate(r) for r in resources]
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
    response_model=ResponseEnvelope[ResourceRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create resource",
    dependencies=[Depends(require_permission(Permission.VENUE_WRITE))],
)
async def create_resource(
    request: Request,
    body: ResourceCreate,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    db: AsyncSession = Depends(get_db_session),
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[ResourceRead]:
    if not check_event_scope(user, body.event_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Event scope mismatch (BR-018)")

    store = get_idempotency_store()
    if idempotency_key:
        cached = store.get(idempotency_key)
        if cached:
            return ResponseEnvelope[ResourceRead].model_validate(cached[1])

    repo = DomainRepository(Resource, db)
    existing = await repo.get_by_id(body.resource_id, event_id=body.event_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Resource {body.resource_id} already exists")

    resource = Resource(
        resource_id=body.resource_id,
        event_id=body.event_id,
        name=body.name,
        category=body.category.value,
        location=body.location,
        quantity=body.quantity,
        assigned_venue_id=body.assigned_venue_id,
        assigned_session_id=body.assigned_session_id,
        metadata_json=body.metadata_json,
    )
    created = await repo.create(
        resource,
        actor_id=user.user_id,
        event_id=body.event_id,
        correlation_id=request.headers.get("X-Correlation-ID"),
    )
    result = ResourceRead.model_validate(created)
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
    "/{resource_id}",
    response_model=ResponseEnvelope[ResourceRead],
    summary="Get resource by ID",
    dependencies=[Depends(require_permission(Permission.VENUE_READ))],
)
async def get_resource(
    resource_id: str,
    request: Request,
    event_id: str | None = None,
    db: AsyncSession = Depends(get_db_session),
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[ResourceRead]:
    target_event = event_id or user.event_id
    repo = DomainRepository(Resource, db)
    resource = await repo.get_by_id(resource_id, event_id=target_event)
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Resource {resource_id} not found")

    if not check_event_scope(user, resource.event_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Event scope mismatch (BR-018)")

    return make_success_envelope(
        ResourceRead.model_validate(resource),
        request_id=str(uuid.uuid4()),
        correlation_id=request.headers.get("X-Correlation-ID"),
        revision=resource.revision,
    )


@router.put(
    "/{resource_id}",
    response_model=ResponseEnvelope[ResourceRead],
    summary="Update resource with optimistic concurrency",
    dependencies=[Depends(require_permission(Permission.VENUE_WRITE))],
)
async def update_resource(
    resource_id: str,
    request: Request,
    body: ResourceUpdate,
    if_match: Annotated[str | None, Header(alias="If-Match")] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    event_id: str | None = None,
    db: AsyncSession = Depends(get_db_session),
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[ResourceRead]:
    target_event = event_id or user.event_id or "evt_kbc2026"
    if not check_event_scope(user, target_event):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Event scope mismatch (BR-018)")

    store = get_idempotency_store()
    if idempotency_key:
        cached = store.get(idempotency_key)
        if cached:
            return ResponseEnvelope[ResourceRead].model_validate(cached[1])

    expected_rev = int(if_match) if if_match and if_match.isdigit() else None
    repo = DomainRepository(Resource, db)
    updates = body.model_dump(exclude_unset=True)
    if "category" in updates and updates["category"] is not None:
        updates["category"] = updates["category"].value

    try:
        updated = await repo.update(
            resource_id,
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

    result = ResourceRead.model_validate(updated)
    response_data = make_success_envelope(
        result,
        request_id=str(uuid.uuid4()),
        correlation_id=request.headers.get("X-Correlation-ID"),
        revision=updated.revision,
    )
    if idempotency_key:
        store.set(idempotency_key, 200, response_data.model_dump(mode="json"))
    return response_data
