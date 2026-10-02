"""Infeasible State and Manual Queue Handler (S3-T5, AT-09, RULE-09, FR-PLAN-005).

When hard constraints (e.g. capacity, capability, availability) cannot be satisfied by any candidate,
the system returns an explicit INFEASIBLE result, logs exact unmet constraints, and presents ranked manual action options.
"""

from __future__ import annotations

from typing import Any

from packages.contracts.planning import (
    InfeasibleResolutionResult,
    ManualActionOption,
    SolverStatus,
)
from services.workers.optimization.config import RuleConfig, get_rule_config


class InfeasibleResolutionHandler:
    """Handles scenarios where no automated resolution satisfies hard constraints."""

    def __init__(self, config: RuleConfig | None = None) -> None:
        self.config = config or get_rule_config()

    def handle_infeasible_session(
        self,
        event_id: str,
        disrupted_entity_id: str,
        session_name: str,
        registrants: int,
        available_candidate_capacities: dict[str, int],
    ) -> InfeasibleResolutionResult:
        unmet_constraints: list[str] = []
        rejected_reasons: list[str] = []

        for venue_name, cap in available_candidate_capacities.items():
            if cap < registrants:
                reason = f"capacity {cap} < {registrants} registered for {session_name}"
                unmet_constraints.append(reason)
                rejected_reasons.append(f"rejected {venue_name}: {reason}")

        # Generate standard ranked manual action recommendations
        manual_action_options = [
            ManualActionOption(
                rank=1,
                title="Split session into two concurrent tracks",
                description="Partition attendee cohort across two adjacent lecture halls (e.g. LH-3 and LH-5) with dual speaker/AV setup.",
                tradeoffs="Requires additional speaker/moderator and AV crew.",
            ),
            ManualActionOption(
                rank=2,
                title="Convert to Live-Stream Overflow Room",
                description=f"Host key attendees in highest capacity hall and broadcast low-latency video feed to secondary hall.",
                tradeoffs="Remote attendees cannot interact directly with stage.",
            ),
            ManualActionOption(
                rank=3,
                title="Reschedule to available evening time slot",
                description="Move session to 18:30–19:30 when higher capacity venues are freed.",
                tradeoffs="May cause itinerary conflicts for registered attendees and keynote speakers.",
            ),
            ManualActionOption(
                rank=4,
                title="Cap registrations and notify waitlisted attendees",
                description="Enforce hard venue capacity limit and send immediate broadcast notifications to excess registrants.",
                tradeoffs="Attendee dissatisfaction and potential negative social media sentiment.",
            ),
        ]

        return InfeasibleResolutionResult(
            event_id=event_id,
            status=SolverStatus.INFEASIBLE,
            disrupted_entity_id=disrupted_entity_id,
            unmet_constraints=unmet_constraints,
            rejected_reasons=rejected_reasons,
            manual_action_options=manual_action_options,
        )
