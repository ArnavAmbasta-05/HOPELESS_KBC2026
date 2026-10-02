"""KoreX API — Transport & Mobility Router (Sprint 8, TRN-001..008, AT-03, TAD §15)."""

from __future__ import annotations

import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from packages.contracts.auth import AuthUser
from packages.contracts.envelope import ResponseEnvelope, make_success_envelope
from packages.contracts.mobility import (
    Route,
    Stop,
    TransportReallocationPlan,
    Trip,
    Vehicle,
)
from services.api.auth.dependencies import get_current_user
from services.api.auth.rbac import Permission, require_permission
from services.workers.transport.service import TransportService

router = APIRouter(prefix="/api/v1/transport", tags=["Transport & Mobility"])

_transport_service = TransportService()


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class DisruptionRequest(BaseModel):
    vehicle_id: str = Field(default="veh_shuttle_02", description="Disrupted vehicle ID")
    reason: str = Field(default="Battery management system warning", description="Disruption reason")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/vehicles",
    response_model=ResponseEnvelope[list[Vehicle]],
    summary="List fleet vehicles with status, capacity, and current location",
)
async def list_vehicles(
    current_user: AuthUser = Depends(require_permission(Permission.TRANSPORT_READ)),
) -> ResponseEnvelope[list[Vehicle]]:
    """Returns active shuttle fleet and standby buses."""
    vehicles = _transport_service.get_vehicles()
    return make_success_envelope(data=vehicles, request_id=str(uuid.uuid4()))


@router.get(
    "/routes",
    response_model=ResponseEnvelope[list[Route]],
    summary="List campus transport routes and estimated durations",
)
async def list_routes(
    current_user: AuthUser = Depends(require_permission(Permission.TRANSPORT_READ)),
) -> ResponseEnvelope[list[Route]]:
    """Returns registered campus links."""
    routes = _transport_service.get_routes()
    return make_success_envelope(data=routes, request_id=str(uuid.uuid4()))


@router.get(
    "/trips",
    response_model=ResponseEnvelope[list[Trip]],
    summary="List scheduled and in-transit trips with cohort mapping",
)
async def list_trips(
    current_user: AuthUser = Depends(require_permission(Permission.TRANSPORT_READ)),
) -> ResponseEnvelope[list[Trip]]:
    """Returns trip schedule."""
    trips = _transport_service.get_trips()
    return make_success_envelope(data=trips, request_id=str(uuid.uuid4()))


@router.post(
    "/disrupt",
    response_model=ResponseEnvelope[TransportReallocationPlan],
    summary="Handle vehicle disruption and execute CP-SAT reallocation (AT-03)",
)
async def handle_transport_disruption(
    request: DisruptionRequest,
    current_user: AuthUser = Depends(require_permission(Permission.TRANSPORT_WRITE)),
) -> ResponseEnvelope[TransportReallocationPlan]:
    """Recalculates capacity, reallocates standby bus, and issues tasks + notices."""
    try:
        plan = _transport_service.handle_transport_disruption(
            disrupted_vehicle_id=request.vehicle_id,
            reason=request.reason,
        )
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return make_success_envelope(data=plan, request_id=str(uuid.uuid4()))
