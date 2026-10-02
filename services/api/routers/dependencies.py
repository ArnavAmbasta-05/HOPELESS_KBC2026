"""Dependencies and Blast Radius API Router (S2, TAD §8, §27)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from packages.contracts.auth import AuthUser
from packages.contracts.envelope import ResponseEnvelope, make_success_envelope
from packages.contracts.graph import BlastRadiusRequest, BlastRadiusResult
from packages.domain.database import get_db_session
from packages.domain.graph.builder import populate_graph_from_seed
from packages.domain.graph.engine import BlastRadiusEngine
from packages.domain.models import DependencyEdge
from sqlalchemy import select, func
from services.api.auth.dependencies import get_current_user
from services.api.auth.rbac import Permission, check_event_scope, require_permission

router = APIRouter(prefix="/api/v1/dependencies", tags=["dependencies"])


@router.post(
    "/blast-radius",
    response_model=ResponseEnvelope[BlastRadiusResult],
    summary="Compute blast radius from disruption node",
    dependencies=[Depends(require_permission(Permission.VENUE_READ))],
)
async def compute_blast_radius(
    request: Request,
    body: BlastRadiusRequest,
    db: AsyncSession = Depends(get_db_session),
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[BlastRadiusResult]:
    if not check_event_scope(user, body.event_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Event scope mismatch (BR-018)",
        )

    # If database has no edges yet for this event, bootstrap from seed
    edge_count_res = await db.execute(
        select(func.count()).select_from(DependencyEdge).where(DependencyEdge.event_id == body.event_id)
    )
    if (edge_count_res.scalar() or 0) == 0:
        await populate_graph_from_seed(db)

    engine = BlastRadiusEngine(db)
    result = await engine.compute_blast_radius(body)

    return make_success_envelope(
        result,
        request_id=str(uuid.uuid4()),
        correlation_id=request.headers.get("X-Correlation-ID"),
    )
