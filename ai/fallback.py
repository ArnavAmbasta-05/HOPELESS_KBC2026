"""LLM Outage Fallback Engine (S5-T6.2, AI-007, TAD §22).

Provides deterministic rule execution and structured templated explanations when the LLM service is unavailable.
"""

from __future__ import annotations

from typing import Any
from ai.explainer import AI_SUMMARY_LABEL, AIExplanationResult


class LLMOutageFallbackHandler:
    """Generates guaranteed deterministic templated explanations during LLM service outages."""

    @staticmethod
    def generate_fallback_summary(
        venue_name: str,
        relocated_count: int,
        at_risk_count: int,
        reason: str,
    ) -> AIExplanationResult:
        """Deterministic templated narrative when LLM provider is unreachable."""
        at_risk_text = f"{at_risk_count} task(s) flagged at risk" if at_risk_count > 0 else "0 tasks at risk"
        narrative = (
            f"[FALLBACK MODE] {venue_name} is unavailable due to: {reason}. "
            f"{relocated_count} sessions have been re-allocated by the deterministic rules engine. "
            f"{at_risk_text}."
        )

        return AIExplanationResult(
            summary_text=narrative,
            label=AI_SUMMARY_LABEL,
            is_ai_generated=True,
            grounding_sources=["fallback:deterministic_template", "tool:venue_resolver"],
            confidence_score=1.0,
            model_name="deterministic-fallback-engine",
            prompt_version="v1.0-fallback",
        )
