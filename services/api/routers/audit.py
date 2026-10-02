"""Audit API Router (S1-T4, BR-015, TAD §18).

Provides read-only access to the append-only Audit Service logs.
No update or delete operations are supported or implemented.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from packages.contracts.auth import AuthUser
from packages.contracts.entities import AuditRecordRead
from packages.contracts.envelope import ResponseEnvelope, make_success_envelope
from packages.domain.database import get_db_session
from packages.domain.models import AuditRecord
from packages.domain.repository import DomainRepository
from services.api.auth.dependencies import get_current_user
from services.api.auth.rbac import Permission, check_event_scope, require_permission

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])


@router.get(
    "",
    response_model=ResponseEnvelope[list[AuditRecordRead]],
    summary="List append-only audit logs",
    dependencies=[Depends(require_permission(Permission.ADMIN_AUDIT))],
)
async def list_audit_logs(
    request: Request,
    event_id: str | None = None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    actor_id: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[list[AuditRecordRead]]:
    target_event = event_id or user.event_id
    if target_event and not check_event_scope(user, target_event):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Event scope mismatch (BR-018)")

    repo = DomainRepository(AuditRecord, db)
    offset = (page - 1) * limit
    filters: dict[str, str] = {}
    if entity_type:
        filters["entity_type"] = entity_type
    if entity_id:
        filters["entity_id"] = entity_id
    if actor_id:
        filters["actor_id"] = actor_id

    logs, total = await repo.list_entities(
        event_id=target_event,
        offset=offset,
        limit=limit,
        filters=filters if filters else None,
    )
    items = [AuditRecordRead.model_validate(log) for log in logs]
    return make_success_envelope(
        items,
        request_id=str(uuid.uuid4()),
        correlation_id=request.headers.get("X-Correlation-ID"),
        page=page,
        limit=limit,
        total=total,
    )
