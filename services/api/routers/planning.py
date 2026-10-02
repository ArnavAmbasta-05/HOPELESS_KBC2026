"""Planning, Optimization, and Rules API Router (Sprint 3, TAD §10, §11)."""

from __future__ import annotations

import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from packages.contracts.auth import AuthUser
from packages.contracts.envelope import ResponseEnvelope, make_success_envelope
from packages.contracts.planning import (
    InfeasibleResolutionResult,
    TaskPlanResult,
    VenueResolutionResult,
    VolunteerReallocationResult,
)
from packages.domain.seed import GoldenSeed, load_golden_seed
from services.api.auth.dependencies import get_current_user
from services.api.auth.rbac import Permission, require_permission
from services.workers.optimization.infeasible import InfeasibleResolutionHandler
from services.workers.optimization.task_planner import TaskPlanner
from services.workers.optimization.venue_resolver import VenueResolver
from services.workers.optimization.volunteer_solver import VolunteerSolver

router = APIRouter(prefix="/api/v1/planning", tags=["Planning & Optimization"])


@router.post(
    "/resolve-venues",
    response_model=ResponseEnvelope[VenueResolutionResult],
    summary="Resolve venue reallocations with retained rejection reasons",
    dependencies=[Depends(require_permission(Permission.VENUE_READ))],
)
async def resolve_venues(
    request: Request,
    unavailable_venue_id: str = "ven_main_aud",
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[VenueResolutionResult]:
    resolver = VenueResolver()
    seed = load_golden_seed()
    result = resolver.resolve_disrupted_sessions(seed=seed, unavailable_venue_id=unavailable_venue_id)
    return make_success_envelope(
        result,
        request_id=str(uuid.uuid4()),
        correlation_id=request.headers.get("X-Correlation-ID"),
    )


@router.post(
    "/reallocate-volunteers",
    response_model=ResponseEnvelope[VolunteerReallocationResult],
    summary="Reallocate volunteers via Google OR-Tools CP-SAT",
    dependencies=[Depends(require_permission(Permission.VOLUNTEER_READ))],
)
async def reallocate_volunteers(
    request: Request,
    disrupted_venue_id: str = "ven_main_aud",
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[VolunteerReallocationResult]:
    solver = VolunteerSolver()
    seed = load_golden_seed()
    result = solver.solve_reallocation(seed=seed, disrupted_venue_id=disrupted_venue_id)
    return make_success_envelope(
        result,
        request_id=str(uuid.uuid4()),
        correlation_id=request.headers.get("X-Correlation-ID"),
    )


@router.post(
    "/generate-tasks",
    response_model=ResponseEnvelope[TaskPlanResult],
    summary="Generate 17 operational follow-up tasks with slack and escalations",
    dependencies=[Depends(require_permission(Permission.PROPOSAL_READ))],
)
async def generate_tasks(
    request: Request,
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[TaskPlanResult]:
    planner = TaskPlanner()
    seed = load_golden_seed()
    result = planner.generate_plan(seed=seed)
    return make_success_envelope(
        result,
        request_id=str(uuid.uuid4()),
        correlation_id=request.headers.get("X-Correlation-ID"),
    )


@router.post(
    "/infeasible-check",
    response_model=ResponseEnvelope[InfeasibleResolutionResult],
    summary="Handle infeasible constraint resolution with ranked manual options",
    dependencies=[Depends(require_permission(Permission.VENUE_READ))],
)
async def infeasible_check(
    request: Request,
    event_id: str = "ev_kbc2026",
    session_id: str = "ses_mega_closing",
    session_name: str = "Mega Closing Ceremony",
    registrants: int = 1200,
    user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[InfeasibleResolutionResult]:
    handler = InfeasibleResolutionHandler()
    result = handler.handle_infeasible_session(
        event_id=event_id,
        disrupted_entity_id=session_id,
        session_name=session_name,
        registrants=registrants,
        available_candidate_capacities={"Open Air Theatre": 600, "Seminar Hall": 250, "LH-3": 150, "LH-5": 120},
    )
    return make_success_envelope(
        result,
        request_id=str(uuid.uuid4()),
        correlation_id=request.headers.get("X-Correlation-ID"),
    )
