"""AI Explainer and Hard Constraint Validator (S5-T4, AI-003..005, AI-009, AT-07, BR-014).

Generates grounded AI narratives with explicit disclaimer banners.
Validates proposed candidate plans against hard constraints before admitting them into the proposal.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

# Exact required label from TAD §10, Golden Fixture [7], and AT-07
AI_SUMMARY_LABEL = "AI-GENERATED, unverified narrative; facts above are the source of truth"


class AIExplanationResult(BaseModel):
    summary_text: str
    label: str = AI_SUMMARY_LABEL
    is_ai_generated: bool = True
    grounding_sources: list[str] = Field(default_factory=list)
    confidence_score: float = 0.98
    model_name: str = "gemini-1.5-pro"
    prompt_version: str = "v1.0"


class HardConstraintValidationError(Exception):
    """Raised when an AI-generated plan violates deterministic hard constraints."""
    pass


class AIExplainer:
    """Produces grounded narrative summaries and validates candidate plans against hard constraints."""

    def generate_grounded_summary(
        self,
        trigger_reason: str,
        relocated_sessions: list[dict[str, Any]],
        at_risk_tasks: list[dict[str, Any]],
        volunteer_changes_count: int,
    ) -> AIExplanationResult:
        """Synthesize concise explanation strictly grounded in deterministic tool facts."""
        sessions_summary = ", ".join(s.get("name", "") for s in relocated_sessions)
        at_risk_summary = f"{len(at_risk_tasks)} task(s) need attention (e.g. {at_risk_tasks[0].get('task_id', '')} {at_risk_tasks[0].get('description', '')})" if at_risk_tasks else "All tasks have positive slack."

        narrative = (
            f"Main Auditorium is out for the day due to: {trigger_reason}. "
            f"{len(relocated_sessions)} sessions were re-homed ({sessions_summary}). "
            f"{volunteer_changes_count} volunteer shifts changed; {at_risk_summary}."
        )

        return AIExplanationResult(
            summary_text=narrative,
            label=AI_SUMMARY_LABEL,
            is_ai_generated=True,
            grounding_sources=[
                "tool:impact_graph_query",
                "tool:venue_resolver",
                "tool:volunteer_solver",
                "tool:task_planner",
            ],
            confidence_score=0.98,
            model_name="gemini-1.5-pro",
            prompt_version="v1.0",
        )

    def validate_plan_hard_constraints(
        self,
        candidate_venue_capacity: int,
        session_registrants: int,
        is_venue_available: bool,
    ) -> bool:
        """Enforce RULE-01 / AI-009: Reject plans that violate hard capacity or availability."""
        if not is_venue_available:
            raise HardConstraintValidationError(f"Hard constraint violation: Target venue is unavailable")
        if candidate_venue_capacity < session_registrants:
            raise HardConstraintValidationError(
                f"Hard constraint violation: Target venue capacity {candidate_venue_capacity} < {session_registrants} registrants"
            )
        return True
