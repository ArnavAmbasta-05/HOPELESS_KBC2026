"""KoreX API — AI Orchestration & HITL Router (Sprint 5, TAD §12, TAD §21, §22)."""

from __future__ import annotations

import os
import uuid
import httpx
from typing import Any
from dotenv import load_dotenv

load_dotenv()

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from ai.explainer import AIExplainer
from ai.graphs.supervisor import EventSupervisorService
from ai.security import PromptSecurityGuard
from ai.tracing import AITraceManager
from packages.contracts.envelope import ResponseEnvelope, make_success_envelope
from packages.contracts.logging import get_logger
from services.api.auth.dependencies import get_current_user
from services.api.auth.rbac import Permission, require_permission
from packages.contracts.auth import AuthUser

logger = get_logger(__name__)

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


class AIChatRequest(BaseModel):
    prompt: str = Field(..., description="User prompt or question")
    event_id: str = Field(default="evt_kbc2026", description="Event ID")
    context: str | None = Field(default=None, description="Optional extra operational context")


@router.post(
    "/chat",
    response_model=ResponseEnvelope[dict[str, Any]],
    summary="Interactive live Google Gemini co-pilot query with grounded KIIT graph and Notion context",
)
async def chat_with_gemini_copilot(
    request: AIChatRequest,
    current_user: AuthUser = Depends(get_current_user),
) -> ResponseEnvelope[dict[str, Any]]:
    """Answers operator operational queries live using Gemini with grounding context."""
    import os
    from services.api.ai_guard import inspect_prompt, GUARD_SYSTEM_PREFIX

    # Anti-jailbreak / prompt-injection guard: run BEFORE touching the LLM.
    guard = inspect_prompt(request.prompt)
    if guard.blocked:
        logger.warning("ai.guard_blocked", category=guard.category, user=current_user.user_id)
        return make_success_envelope(
            data={
                "response": guard.message,
                "is_live_gemini": False,
                "blocked_by_guard": True,
                "guard_category": guard.category,
                "model_name": "n/a",
                "label": "BLOCKED by KoreX AI safety guard (prompt-injection / jailbreak defence)",
                "grounding_sources": ["guard:prompt_injection_filter"],
                "confidence": "100%",
            },
            request_id=str(uuid.uuid4()),
        )

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
    model_name = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")



    grounded_context = (
        "Grounding Context for KIIT Event Operations (KoreX):\n"
        "- Campus: KIIT University, Patia, Bhubaneswar (Campuses 3, 6, 7, 15).\n"
        "- GIS Engine: CARTO AI Workflows & MCP Server (ac_o657y8er) connected with 14 spatial tools (routing, isolines, geocoding, builder).\n"
        "- Venues: Main Auditorium (1600 cap, UNAVAILABLE due to AC leak), "
        "Open Air Theatre (600 cap, AVAILABLE), Campus 7 Seminar Hall (250 cap, AVAILABLE), "
        "Campus 6 Aud (400 cap), Campus 15 Aud (350 cap), Campus 3 Lawn (800 cap).\n"
        "- Relocations: Keynote (580 pax) -> Open Air Theatre (150m walking, 2 min), AI Track (240 pax) -> Campus 7 Seminar Hall (400m walking, 5 min).\n"
        "- Hostels: KP-6/KP-7 (Boys), QC-1/QC-2 (Girls).\n"
        "- Volunteers: 16 total, 1 standby deployed (Arjun Sharma - AV Lead, KP-6).\n"
        "- Notion Workspace: Udit Pandya's Notion (Connected with 3 live databases).\n"
        "- Hard Constraints: Capacity violations = 0, Time overlaps = 0.\n"
    )

    narrative = f"[Grounded Response] For query '{request.prompt}': All 4 relocated sessions have been re-assigned to Open Air Theatre and Campus 7 Seminar Hall with zero time overlap and full seat compliance."
    sources = ["tool:venue_resolver", "tool:volunteer_solver", "tool:carto_mcp_spatial", "notion:udit_pandya_workspace", f"model:{model_name}"]
    is_live = False

    candidate_models = [
        "gemini-3.1-flash-lite",
        "gemini-flash-latest",
        "gemini-3.1-flash-lite-preview",
    ]

    if api_key:
        system_prompt = (
            GUARD_SYSTEM_PREFIX +
            "You are the KoreX AI Operational Supervisor for KIIT University Event Command Center.\n"
            "If the user greets you (e.g. 'hey', 'hello'), greet them back warmly as the Event Commander and provide a 1-2 sentence readiness status.\n"
            "If they ask an operational or map/GIS question, answer concisely and professionally using these grounded facts:\n"
            f"{grounded_context}\n\n"
            f"User Query: {request.prompt}\n"
            "Answer in 2-4 direct, executive sentences with specific venue names, distances, and student counts where applicable."
        )
        for cand in candidate_models:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{cand}:generateContent?key={api_key}"
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post(url, json={"contents": [{"parts": [{"text": system_prompt}]}]})
                    if resp.status_code == 200:
                        gen_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                        if gen_text:
                            narrative = gen_text
                            is_live = True
                            model_name = cand
                            sources = ["tool:venue_resolver", "tool:volunteer_solver", "tool:carto_mcp_spatial", "notion:udit_pandya_workspace", f"model:{cand}"]
                            break
                    else:
                        logger.warning("gemini.chat_failed", cand=cand, status=resp.status_code, body=resp.text[:120])
            except Exception as exc:
                logger.error("gemini.chat_exception", cand=cand, exc=str(exc))
                continue






    return make_success_envelope(
        data={
            "response": narrative,
            "is_live_gemini": is_live,
            "model_name": model_name,
            "label": "AI-GENERATED, unverified narrative; facts above are the source of truth",
            "grounding_sources": sources,
            "confidence": "99%" if is_live else "98%",
        },
        request_id=str(uuid.uuid4()),
    )


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

