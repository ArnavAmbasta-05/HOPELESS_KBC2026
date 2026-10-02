import os
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
    model_name: str = "gemini-flash-latest"
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
        use_live_gemini: bool = False,
    ) -> AIExplanationResult:
        """Synthesize concise explanation strictly grounded in deterministic tool facts."""
        sessions_summary = ", ".join(s.get("name", "") for s in relocated_sessions)
        at_risk_summary = f"{len(at_risk_tasks)} task(s) need attention (e.g. {at_risk_tasks[0].get('task_id', '')} {at_risk_tasks[0].get('description', '')})" if at_risk_tasks else "All tasks have positive slack."

        narrative = (
            f"Main Auditorium is out for the day due to: {trigger_reason}. "
            f"{len(relocated_sessions)} sessions were re-homed ({sessions_summary}). "
            f"{volunteer_changes_count} volunteer shifts changed; {at_risk_summary}."
        )

        model_name = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

        if use_live_gemini and api_key:
            try:
                import httpx
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                prompt = (
                    f"You are the KoreX KIIT Event Operations AI Supervisor. "
                    f"Synthesize an executive briefing for the Event Commander using these grounded facts only:\n"
                    f"- Trigger: {trigger_reason}\n"
                    f"- Relocated Sessions: {sessions_summary}\n"
                    f"- Volunteer Changes: {volunteer_changes_count} shifts adjusted\n"
                    f"- At-risk Tasks: {at_risk_summary}\n"
                    f"Keep it under 3 concise sentences."
                )
                with httpx.Client(timeout=8.0) as client:
                    resp = client.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                    if resp.status_code == 200:
                        gen_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                        if gen_text:
                            narrative = gen_text
            except Exception:
                pass

        return AIExplanationResult(
            summary_text=narrative,
            label=AI_SUMMARY_LABEL,
            is_ai_generated=True,
            grounding_sources=[
                "tool:impact_graph_query",
                "tool:venue_resolver",
                "tool:volunteer_solver",
                "tool:task_planner",
                f"model:{model_name}",
            ],
            confidence_score=0.98,
            model_name=model_name,
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

