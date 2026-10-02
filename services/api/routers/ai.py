"""KoreX API — AI Orchestration & HITL Router (Sprint 5, TAD §12, TAD §21, §22)."""

from __future__ import annotations

import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from ai.explainer import AIExplainer
from ai.graphs.supervisor import EventSupervisorService
from ai.security import PromptSecurityGuard
from ai.tracing import AITraceManager
from packages.contracts.envelope import ResponseEnvelope, make_success_envelope
from services.api.auth.dependencies import get_current_user
from services.api.auth.rbac import Permission, require_permission
from packages.contracts.auth import AuthUser

router = APIRouter(prefix="/api/v1/ai", tags=["AI Orchestration"])

_supervisor_service = EventSupervisorService()
_trace_manager = AITraceManager()


# ---------------------------------------------------------------------------
# Request / Response Schemas
# ---------------------------------------------------------------------------

class StartRunRequest(BaseModel):
    event_id: str = Field(default="evt_kbc2026", description="Event ID")
    venue_id: str = Field(default="ven_main_aud", description="Disrupted venue ID")
    reason: str = Field(default="Ceiling AC leak reported by Estate Office", description="Disruption trigger reason")


class ResumeRunRequest(BaseModel):
    approved: bool = Field(..., description="Approval decision (true = commit, false = reject)")
    rejection_reason: str | None = Field(default=None, description="Optional reason if rejected")


class ExplainRequest(BaseModel):
    trigger_reason: str = Field(..., description="Disruption trigger description")
    relocated_sessions: list[dict[str, Any]] = Field(default_factory=list, description="List of session relocations")
    at_risk_tasks: list[dict[str, Any]] = Field(default_factory=list, description="At-risk tasks")
    volunteer_changes_count: int = Field(default=5, description="Count of volunteer shifts changed")


class AIResponseData(BaseModel):
    thread_id: str
    run_id: str
    approval_status: str
    ai_summary: str | None = None
    is_ai_generated: bool = True
    model_metadata: dict[str, Any] = Field(default_factory=dict)
    impacted_nodes: list[str] = Field(default_factory=list)
    selected_plan: dict[str, Any] | None = None
    external_writes: list[dict[str, Any]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/runs",
    response_model=ResponseEnvelope[AIResponseData],
    summary="Start an AI supervisor orchestration run (HITL interrupt before commit)",
)
async def start_orchestration_run(
    request: StartRunRequest,
    current_user: AuthUser = Depends(require_permission(Permission.PROPOSAL_READ)),
) -> ResponseEnvelope[AIResponseData]:
    """Starts the LangGraph supervisor workflow up to the HITL approval interrupt."""
    thread_id, state = _supervisor_service.start_orchestration_run(
        event_id=request.event_id,
        venue_id=request.venue_id,
        reason=request.reason,
    )

    data = AIResponseData(
        thread_id=thread_id,
        run_id=state.get("run_id", ""),
        approval_status=state.get("approval_status", "pending_approval"),
        ai_summary=state.get("ai_summary"),
        is_ai_generated=state.get("is_ai_generated", True),
        model_metadata=state.get("model_metadata", {}),
        impacted_nodes=state.get("impacted_nodes", []),
        selected_plan=state.get("selected_plan"),
        external_writes=state.get("external_writes", []),
    )
    return make_success_envelope(data=data, request_id=str(uuid.uuid4()))


@router.post(
    "/runs/{thread_id}/resume",
    response_model=ResponseEnvelope[AIResponseData],
    summary="Resume an interrupted AI supervisor run with human approval/rejection",
)
async def resume_orchestration_run(
    thread_id: str,
    request: ResumeRunRequest,
    current_user: AuthUser = Depends(require_permission(Permission.PROPOSAL_APPROVE)),
) -> ResponseEnvelope[AIResponseData]:
    """Resumes the interrupted LangGraph thread to commit or cleanly reject."""
    final_state = _supervisor_service.resume_orchestration_run(
        thread_id=thread_id,
        approved=request.approved,
        approved_by=current_user.email or current_user.user_id,
        rejection_reason=request.rejection_reason,
    )

    data = AIResponseData(
        thread_id=thread_id,
        run_id=final_state.get("run_id", ""),
        approval_status=final_state.get("approval_status", "committed"),
        ai_summary=final_state.get("ai_summary"),
        is_ai_generated=final_state.get("is_ai_generated", True),
        model_metadata=final_state.get("model_metadata", {}),
        impacted_nodes=final_state.get("impacted_nodes", []),
        selected_plan=final_state.get("selected_plan"),
        external_writes=final_state.get("external_writes", []),
    )
    return make_success_envelope(data=data, request_id=str(uuid.uuid4()))


@router.post(
    "/explain",
    response_model=ResponseEnvelope[dict[str, Any]],
    summary="Generate deterministic grounded AI explanation with mandatory banner",
)
async def generate_explanation(
    request: ExplainRequest,
    current_user: AuthUser = Depends(require_permission(Permission.PROPOSAL_READ)),
) -> ResponseEnvelope[dict[str, Any]]:
    """Generate grounded explanation labeled with AT-07 disclaimer."""
    explainer = AIExplainer()
    explanation = explainer.generate_grounded_summary(
        trigger_reason=request.trigger_reason,
        relocated_sessions=request.relocated_sessions,
        at_risk_tasks=request.at_risk_tasks,
        volunteer_changes_count=request.volunteer_changes_count,
    )

    data = {
        "summary_text": explanation.summary_text,
        "label": explanation.label,
        "is_ai_generated": explanation.is_ai_generated,
        "model_name": explanation.model_name,
        "confidence_score": explanation.confidence_score,
        "grounding_sources": explanation.grounding_sources,
    }
    return make_success_envelope(data=data, request_id=str(uuid.uuid4()))
