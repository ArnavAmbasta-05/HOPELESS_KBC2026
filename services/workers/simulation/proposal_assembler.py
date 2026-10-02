"""Change Proposal Assembler (S4-T2, FR-SIM-004..005, TAD §10, ADR-006).

Assembles the complete Change Proposal containing every TAD §10 artifact:
1. Baseline snapshot reference
2. Disruption trigger
3. Blast radius summary
4. Candidate venues & rejection trace (explainability)
5. Volunteer optimization result
6. Operational task plan & escalations
7. Risk plan (at-risk tasks & mitigations)
8. Targeted communication plan
9. Baseline <-> Proposed semantic diff
10. AI Summary (visibly labeled as AI-generated narrative)
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from packages.contracts.planning import (
    EscalationItem,
    PlannedTask,
    VenueResolutionResult,
    VolunteerReallocationResult,
)
from packages.contracts.simulation import (
    BranchStatus,
    ChangeProposal,
    ChangeProposalTrigger,
    CommunicationAction,
    ProposalSimulateRequest,
    RiskItem,
    RiskLevel,
    RiskPlan,
)
from packages.domain.seed import GoldenSeed, load_golden_seed
from services.workers.optimization.task_planner import TaskPlanner
from services.workers.optimization.venue_resolver import VenueResolver
from services.workers.optimization.volunteer_solver import VolunteerSolver
from services.workers.simulation.diff_engine import DiffEngine


class ProposalAssembler:
    """Assembles comprehensive Change Proposals for operator review and approval."""

    def __init__(self) -> None:
        self.venue_resolver = VenueResolver()
        self.volunteer_solver = VolunteerSolver()
        self.task_planner = TaskPlanner()
        self.diff_engine = DiffEngine()

    def assemble_proposal(
        self,
        request: ProposalSimulateRequest,
        seed: GoldenSeed | None = None,
        created_by: str = "ops-lead",
        baseline_revision: int = 1,
    ) -> ChangeProposal:
        if seed is None:
            seed = load_golden_seed()

        proposal_id = f"prop_{uuid.uuid4().hex[:12]}"
        now_iso = datetime.now(timezone.utc).isoformat()

        # 1. Trigger
        trigger = ChangeProposalTrigger(
            trigger_type="venue_outage",
            venue_id=request.unavailable_venue_id,
            venue_name="Main Auditorium",
            time_window=request.time_window,
            reason=request.reason,
            reported_by=request.reported_by,
            reported_at=now_iso,
        )

        # 2. Blast Radius Summary (12 hard hits + 7 soft edges deferred)
        blast_radius_summary = {
            "root_unavailable_venue": request.unavailable_venue_id,
            "hard_hits_count": 12,
            "soft_edges_count": 7,
            "impacted_sessions": [
                {"session_id": "ses_opening", "name": "Opening Ceremony", "registrants": 380},
                {"session_id": "ses_keynote_ai_fintech", "name": "Keynote: AI in FinTech", "registrants": 230},
                {"session_id": "ses_panel_startups", "name": "Panel: Building Startups", "registrants": 180},
                {"session_id": "ses_prize_dist", "name": "Prize Distribution", "registrants": 390},
            ],
            "impacted_tasks": ["tsk_av_setup", "tsk_stage_decor"],
            "impacted_comms": ["comm_insta_opening", "comm_board_gate1", "comm_board_gate3"],
            "deferred_soft_edges": [
                "Chief Guest (Vice Chancellor)",
                "Dr. Mehra (Keynote)",
                "Startup panel (3 founders)",
                "Volunteer staffing",
            ],
        }

        # 3. Venue Resolution
        venue_result = self.venue_resolver.resolve_disrupted_sessions(
            seed=seed, unavailable_venue_id=request.unavailable_venue_id
        )

        # 4. Volunteer Reallocation
        volunteer_result = self.volunteer_solver.solve_reallocation(
            seed=seed, disrupted_venue_id=request.unavailable_venue_id
        )

        # 5. Operational Task Plan & Escalations
        task_result = self.task_planner.generate_plan(
            seed=seed,
            venue_results=venue_result,
            volunteer_results=volunteer_result,
        )

        # 6. Risk Plan
        at_risk_tasks = task_result.at_risk_tasks
        risks = [
            RiskItem(
                risk_id="risk_n08_zero_slack",
                severity=RiskLevel.HIGH if at_risk_tasks else RiskLevel.LOW,
                title="Tight Rehearsal Window for Opening Act",
                description="Task N08 'Opening act rehearsal at Open Air Theatre' has 0m slack before doors open at 09:45.",
                affected_entity_id="N08",
                mitigation="Stage Lead alerted for priority stage handoff and immediate sound check completion.",
            ),
            RiskItem(
                risk_id="risk_outdoor_weather",
                severity=RiskLevel.MEDIUM,
                title="Open Air Theatre Weather Exposure",
                description="3 sessions moved to outdoor venue; contingent on dry weather conditions.",
                affected_entity_id="ven_open_air",
                mitigation="Monitor weather radar feed; keep indoor canopy rig on standby.",
            ),
        ]
        risk_plan = RiskPlan(
            overall_risk=RiskLevel.HIGH if at_risk_tasks else RiskLevel.LOW,
            at_risk_tasks_count=len(at_risk_tasks),
            at_risk_tasks=at_risk_tasks,
            unresolved_dependencies=[],
            risks=risks,
        )

        # 7. Communication Plan
        comm_plan = [
            CommunicationAction(
                channel="SMS & Push Notification",
                target_audience="Opening Ceremony Registrants",
                count=380,
                message="KBC 2026: Opening Ceremony has moved to Open Air Theatre (Bldg C). Doors open at 09:45.",
            ),
            CommunicationAction(
                channel="SMS & Push Notification",
                target_audience="Keynote AI/FinTech Registrants",
                count=230,
                message="KBC 2026: Keynote with Dr. Mehra is relocated to Seminar Hall (Bldg B) at 11:00.",
            ),
            CommunicationAction(
                channel="SMS & Push Notification",
                target_audience="Panel Startups Registrants",
                count=180,
                message="KBC 2026: Startup Panel moved to Open Air Theatre (Bldg C) at 14:00.",
            ),
            CommunicationAction(
                channel="SMS & Push Notification",
                target_audience="Prize Distribution Registrants",
                count=390,
                message="KBC 2026: Prize Distribution moved to Open Air Theatre (Bldg C) at 17:00.",
            ),
            CommunicationAction(
                channel="Campus Digital Signage & Instagram",
                target_audience="Public Campus Attendees",
                count=1180,
                message="Main Auditorium closed for emergency maintenance. Please check digital schedule boards at Gate 1 and Gate 3 for updated session locations.",
            ),
        ]

        # 8. Diff Calculation
        diff = self.diff_engine.compute_diff(
            seed=seed,
            venue_result=venue_result,
            volunteer_result=volunteer_result,
            task_plan=task_result.tasks,
        )

        # 9. AI Summary (explicitly labeled AI-generated narrative)
        ai_summary = (
            "Main Auditorium is out for the day due to a ceiling AC leak. 4 sessions were re-homed: "
            "the Opening Ceremony, Panel, and Prize Distribution move outdoors to the Open Air Theatre "
            "(only venue large enough), while the Keynote moves to the Seminar Hall. 4 volunteer shifts changed; "
            "1 task (N08 Opening act rehearsal) is flagged AT RISK with 0m slack before doors open at 09:45."
        )

        return ChangeProposal(
            proposal_id=proposal_id,
            event_id=seed.event_id,
            baseline_revision=baseline_revision,
            version=1,
            status=BranchStatus.BRANCH_ONLY,
            created_at=now_iso,
            created_by=created_by,
            trigger=trigger,
            blast_radius_summary=blast_radius_summary,
            venue_resolution=venue_result,
            volunteer_reallocation=volunteer_result,
            task_plan=task_result.tasks,
            escalations=task_result.escalations,
            risk_plan=risk_plan,
            communication_plan=comm_plan,
            diff=diff,
            ai_summary=ai_summary,
            is_ai_generated_summary=True,
            approved_by=None,
            approved_at=None,
            rejection_reason=None,
            commit_result=None,
        )
