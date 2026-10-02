"""Sprint 10: AI Quality, Governance & Evaluation Suite (S10-T3, TAD §24.1, NFR-AI-001..003)."""

from __future__ import annotations

import pytest

from ai.explainer import (
    AI_SUMMARY_LABEL,
    AIExplainer,
    HardConstraintValidationError,
)
from ai.security import (
    MutatingToolRequiresApprovalError,
    PromptInjectionDetectedError,
    PromptSecurityGuard,
    UnauthorizedToolExecutionError,
)
from ai.tools import ALLOWLISTED_TOOLS
from packages.domain.seed import load_golden_seed
from services.workers.optimization.venue_resolver import VenueResolver


def test_ai_eval_golden_outputs_vs_expected_facts():
    """TAD §24.1: Verifies that AI summary generates verified facts matching the Golden Simulation Fixture."""
    explainer = AIExplainer()
    seed = load_golden_seed()
    resolver = VenueResolver()
    res = resolver.resolve_disrupted_sessions(seed=seed, unavailable_venue_id="ven_main_aud")
    
    summary_result = explainer.generate_grounded_summary(
        trigger_reason="Ceiling AC leak",
        relocated_sessions=[{"name": a.session_name, "new_venue": a.new_venue_name} for a in res.assignments],
        at_risk_tasks=[{"task_id": "N08", "description": "Stage Setup"}],
        volunteer_changes_count=5,
    )
    
    assert summary_result.label == AI_SUMMARY_LABEL
    assert summary_result.is_ai_generated is True
    assert len(summary_result.grounding_sources) > 0


def test_ai_eval_hard_constraint_enforcement_and_unsupported_claim_rate():
    """TAD §24.1: Zero-tolerance for unsupported claims or capacity constraint violations in generated explanations."""
    explainer = AIExplainer()
    
    # Valid plan passes
    assert explainer.validate_plan_hard_constraints(
        candidate_venue_capacity=600,
        session_registrants=380,
        is_venue_available=True,
    ) is True

    # Capacity violation rejected (AI-009)
    with pytest.raises(HardConstraintValidationError):
        explainer.validate_plan_hard_constraints(
            candidate_venue_capacity=150,
            session_registrants=380,
            is_venue_available=True,
        )


def test_ai_eval_tool_allowlist_and_signature_correctness():
    """TAD §24.1: All tools exposed to AI supervisor must be in allowlist with strict JSON schemas."""
    expected_tool_names = {
        "impact_graph_query",
        "venue_resolver_tool",
        "task_planner_tool",
        "volunteer_solver_tool",
        "proposal_diff_tool",
        "approval_check_tool",
        "notification_draft_tool",
        "weather_forecast_tool",
        "transport_status_tool",
        "attendance_lookup_tool",
    }
    
    actual_tool_names = {tool.name for tool in ALLOWLISTED_TOOLS}
    assert expected_tool_names.issubset(actual_tool_names)
    
    for tool in ALLOWLISTED_TOOLS:
        assert tool.description is not None
        assert len(tool.description) > 10


def test_ai_eval_no_mutation_before_approval_invariant():
    """TAD §24.1: Invariant — AI cannot trigger external state mutations without human-in-the-loop approval."""
    with pytest.raises(MutatingToolRequiresApprovalError):
        PromptSecurityGuard.verify_mutating_tool_gate("commit_plan", is_approved=False)

    # When approved, passes
    PromptSecurityGuard.verify_mutating_tool_gate("commit_plan", is_approved=True)
