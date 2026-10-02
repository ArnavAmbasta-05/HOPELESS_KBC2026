"""KoreX API — Crowd Safety & Flows Router (Sprint 8, CRD-001..007, AT-04/05, TAD §16)."""

from __future__ import annotations

import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from packages.contracts.auth import AuthUser
from packages.contracts.crowd import (
    CrowdAdvisory,
    CrowdAlert,
    CrowdZone,
    Gate,
    RerouteProposal,
)
from packages.contracts.envelope import ResponseEnvelope, make_success_envelope
from services.api.auth.dependencies import get_current_user
from services.api.auth.rbac import Permission, require_permission
from services.workers.crowd.service import CrowdSafetyService

router = APIRouter(prefix="/api/v1/crowd", tags=["Crowd Safety & Flows"])

_crowd_service = CrowdSafetyService()


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class IngestCountRequest(BaseModel):
    zone_id: str = Field(..., description="Zone ID")
    headcount: int = Field(..., ge=0, description="Anonymous measured headcount")


class EvaluateSurgeRequest(BaseModel):
    zone_id: str = Field(default="corridor_link_c6_c7", description="Corridor zone ID")
    surge_count: int = Field(default=270, description="Measured surge headcount")


class TriggerAdvisoryRequest(BaseModel):
    venue_id: str = Field(default="ven_oat", description="Venue ID")
    venue_name: str = Field(default="Open Air Theatre", description="Venue Name")
    current_headcount: int = Field(default=570, description="Current headcount")
    max_capacity: int = Field(default=600, description="Max safe capacity")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/zones",
    response_model=ResponseEnvelope[list[CrowdZone]],
    summary="List crowd monitoring zones and current occupancy ratios",
)
async def list_zones(
    current_user: AuthUser = Depends(require_permission(Permission.CROWD_READ)),
) -> ResponseEnvelope[list[CrowdZone]]:
    """Returns crowd zones with capacity threshold ratios."""
    zones = _crowd_service.get_zones()
    return make_success_envelope(data=zones, request_id=str(uuid.uuid4()))


@router.get(
    "/gates",
    response_model=ResponseEnvelope[list[Gate]],
    summary="List entry/exit gates with flow rates",
)
async def list_gates(
    current_user: AuthUser = Depends(require_permission(Permission.CROWD_READ)),
) -> ResponseEnvelope[list[Gate]]:
    """Returns gate list and flow metrics."""
    gates = _crowd_service.get_gates()
    return make_success_envelope(data=gates, request_id=str(uuid.uuid4()))


@router.get(
    "/alerts",
    response_model=ResponseEnvelope[list[CrowdAlert]],
    summary="List active crowd alerts and threshold breach events",
)
async def list_alerts(
    current_user: AuthUser = Depends(require_permission(Permission.CROWD_READ)),
) -> ResponseEnvelope[list[CrowdAlert]]:
    """Returns active crowd alerts."""
    alerts = _crowd_service.get_alerts()
    return make_success_envelope(data=alerts, request_id=str(uuid.uuid4()))


@router.post(
    "/anonymous-count",
    response_model=ResponseEnvelope[dict[str, Any]],
    summary="Ingest anonymous headcount and evaluate thresholds (CRD-006)",
)
async def ingest_anonymous_count(
    request: IngestCountRequest,
    current_user: AuthUser = Depends(require_permission(Permission.CROWD_WRITE)),
) -> ResponseEnvelope[dict[str, Any]]:
    """Ingests count without identity tracking."""
    try:
        zone, alert = _crowd_service.ingest_anonymous_count(request.zone_id, request.headcount)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return make_success_envelope(
        data={"zone": zone, "alert": alert},
        request_id=str(uuid.uuid4()),
    )


@router.post(
    "/evaluate-surge",
    response_model=ResponseEnvelope[dict[str, Any]],
    summary="Evaluate corridor bottleneck and generate reroute proposal (AT-04)",
)
async def evaluate_surge(
    request: EvaluateSurgeRequest,
    current_user: AuthUser = Depends(require_permission(Permission.CROWD_WRITE)),
) -> ResponseEnvelope[dict[str, Any]]:
    """Generates AT-04 corridor bottleneck alert and gate reroute proposal."""
    alert, proposal = _crowd_service.evaluate_corridor_surge_and_propose_reroute(
        zone_id=request.zone_id,
        surge_count=request.surge_count,
    )
    return make_success_envelope(
        data={"alert": alert, "proposal": proposal},
        request_id=str(uuid.uuid4()),
    )


@router.post(
    "/advisory",
    response_model=ResponseEnvelope[CrowdAdvisory],
    summary="Trigger venue capacity warning/surge advisory (AT-05)",
)
async def trigger_advisory(
    request: TriggerAdvisoryRequest,
    current_user: AuthUser = Depends(require_permission(Permission.CROWD_WRITE)),
) -> ResponseEnvelope[CrowdAdvisory]:
    """Issues capacity advisory when venue approaches maximum safe occupancy."""
    advisory = _crowd_service.trigger_venue_capacity_advisory(
        venue_id=request.venue_id,
        venue_name=request.venue_name,
        current_headcount=request.current_headcount,
        max_capacity=request.max_capacity,
    )
    return make_success_envelope(data=advisory, request_id=str(uuid.uuid4()))
