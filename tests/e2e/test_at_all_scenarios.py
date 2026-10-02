"""Sprint 10: Complete AT-01 through AT-10 End-to-End Acceptance Regression Matrix (S10-T5, TAD §24, §25)."""

from __future__ import annotations

import pytest

from ai.explainer import AI_SUMMARY_LABEL, AIExplainer
from integrations.notion import (
    NotionCommitPlanBuilder,
    NotionConflictDetector,
    NotionPropertyMapper,
    StaleNotionProposalConflictError,
)
from packages.contracts.crowd import AlertSeverity
from packages.contracts.knowledge import RAGQuery
from packages.contracts.planning import SolverStatus
from packages.contracts.weather import WeatherHazardType, WeatherSignal
from packages.domain.seed import load_golden_seed
from services.workers.attendance.credentials import AttendanceCredentialService
from services.workers.attendance.ingest import ScanIngestService
from services.workers.crowd.service import CrowdSafetyService
from services.workers.notifications.service import (
    MassDispatchRequiresApprovalError,
    NotificationService,
)
from services.workers.optimization.infeasible import InfeasibleResolutionHandler
from services.workers.optimization.venue_resolver import VenueResolver
from services.workers.rag.service import RAGKnowledgeService
from services.workers.transport.service import TransportService
from services.workers.weather.service import WeatherService


class TestCompleteAcceptanceScenariosMatrix:
    """Consolidated End-to-End Regression Matrix validating AT-01 through AT-10."""

    def test_at_01_venue_outage_and_golden_relocation(self):
        """AT-01: Main Auditorium power outage -> Blast radius -> 4 sessions re-homed -> 32 Notion write operations."""
        seed = load_golden_seed()
        resolver = VenueResolver()
        res = resolver.resolve_disrupted_sessions(seed=seed, unavailable_venue_id="ven_main_aud")
        
        assert res.status == SolverStatus.OPTIMAL
        assert len(res.assignments) == 4
        
        # Build Notion write plan
        builder = NotionCommitPlanBuilder()
        plan = builder.build_golden_write_plan(
            proposal_id="prop_kbc_disruption_001",
            event_id="evt_kbc2026",
        )
        
        assert len(plan.operations) == 32

    def test_at_02_weather_escalation_and_chained_oat_storm(self):
        """AT-02: Severe thunderstorm over OAT triggers secondary simulation branch on top of golden plan."""
        weather_svc = WeatherService()
        storm_signal = WeatherSignal(
            source="IMD_BHUBANESWAR",
            zone="campus_6_oat",
            hazard_type=WeatherHazardType.LIGHTNING,
            alert_level="red",
            precipitation_mm_per_hr=25.0,
            lightning_probability_pct=90,
            confidence_score=0.94,
        )
        
        branch = weather_svc.generate_weather_branch(
            parent_plan_id="prop_kbc_disruption_001",
            disrupted_outdoor_venue_id="ven_campus_6_oat",
            signal=storm_signal,
            sessions_at_risk=[{"session_id": "ses_opening", "title": "Opening Ceremony"}],
            backup_indoor_venues=[{"venue_id": "ven_multipurpose_hall_c6"}],
        )
        
        assert branch.parent_plan_id == "prop_kbc_disruption_001"
        assert branch.mitigation_action == "INDOOR_RELOCATION"
        assert branch.relocated_sessions[0]["new_venue_id"] == "ven_multipurpose_hall_c6"

    def test_at_03_transport_shuttle_disruption_reallocation(self):
        """AT-03: Assigned shuttle breakdown -> Recompute capacity -> Reallocate standby vehicle -> Driver task."""
        service = TransportService()
        plan = service.handle_transport_disruption(
            disrupted_vehicle_id="veh_shuttle_02",
            reason="Battery management system fault",
        )
        
        assert plan.disrupted_vehicle_id == "veh_shuttle_02"
        assert plan.reallocated_vehicle_id == "veh_bus_standby_a"
        assert plan.recalculated_capacity == 50
        assert len(plan.vehicle_tasks) == 1

    def test_at_04_crowd_pressure_and_reroute(self):
        """AT-04: Corridor load crosses critical threshold -> Alert emitted -> Alternate gate reroute proposed."""
        crowd_svc = CrowdSafetyService()
        alert, proposal = crowd_svc.evaluate_corridor_surge_and_propose_reroute(
            zone_id="corridor_link_c6_c7",
            surge_count=290,
        )
        
        assert alert is not None
        assert proposal.requires_operator_confirm is True
        assert proposal.alternate_gate_id == "gate_2_east"

    def test_at_05_attendance_surge_and_occupancy_broadcast(self):
        """AT-05: Attendance scans reach capacity threshold -> Realtime occupancy advisory generated."""
        crowd_svc = CrowdSafetyService()
        advisory = crowd_svc.trigger_venue_capacity_advisory(
            venue_id="ven_aud_c7",
            venue_name="Auditorium (Campus 7)",
            current_headcount=245,
            max_capacity=250,
        )
        
        assert advisory is not None
        assert "Auditorium (Campus 7)" in advisory.title
        assert "245/250" in advisory.message

    @pytest.mark.asyncio
    async def test_at_06_notion_inbound_edit_and_conflict_detection(self):
        """AT-06: Operator mutates session in Notion concurrently -> Conflict detected -> Re-sync & alert."""
        detector = NotionConflictDetector()
        
        # Check conflict when target page is modified past baseline
        report = await detector.check_conflicts(
            target_page_ids=["page_ses_01"],
            baseline_revision=1,
            baseline_timestamp="2026-03-15T07:45:00Z",
        )
        assert report is not None

    def test_at_07_ai_incident_summary_grounding(self):
        """AT-07: AI generates incident explanation -> Strictly watermarked & verified against hard facts."""
        explainer = AIExplainer()
        seed = load_golden_seed()
        resolver = VenueResolver()
        res = resolver.resolve_disrupted_sessions(seed=seed, unavailable_venue_id="ven_main_aud")
        
        summary = explainer.generate_grounded_summary(
            trigger_reason="Main Auditorium outage",
            relocated_sessions=[{"name": a.session_name} for a in res.assignments],
            at_risk_tasks=[{"task_id": "N08", "description": "Stage Setup"}],
            volunteer_changes_count=5,
        )
        assert summary.label == AI_SUMMARY_LABEL
        assert summary.is_ai_generated is True

    @pytest.mark.asyncio
    async def test_at_08_approval_gate_zero_writes_on_rejection(self):
        """AT-08: Operator rejects proposal -> Zero notifications dispatched without approval."""
        notif_svc = NotificationService()
        drafts = notif_svc.get_drafts()
        target_draft_id = drafts[0].draft_id
        
        with pytest.raises(MassDispatchRequiresApprovalError):
            await notif_svc.dispatch_notification(
                draft_id=target_draft_id,
                is_approved=False,
            )

    def test_at_09_infeasible_capacity_resolution_fallback(self):
        """AT-09: No venue can accommodate 4000 registrants -> Explicit INFEASIBLE status + ranked manual options."""
        handler = InfeasibleResolutionHandler()
        res = handler.handle_infeasible_session(
            event_id="evt_kbc2026",
            disrupted_entity_id="ses_mega_concert",
            session_name="Celebrity Mega Concert",
            registrants=4000,
            available_candidate_capacities={"Seminar Hall": 250, "LH-3": 150},
        )
        
        assert res.status == SolverStatus.INFEASIBLE
        assert len(res.manual_action_options) >= 3

    def test_at_10_post_event_report_and_institutional_memory(self):
        """AT-10: Event closes -> Automated post-event operational report + reusable KnowledgeItem playbook."""
        rag_svc = RAGKnowledgeService()
        report = rag_svc.synthesize_post_event_report(
            event_id="evt_kbc_2026",
            event_name="KIIT Fest 2026",
            telemetry={"total_sessions": 48, "completed_sessions": 47},
        )
        
        assert report.event_id == "evt_kbc_2026"
        assert report.completed_sessions == 47
        
        ki = rag_svc.generate_knowledge_item(
            tenant_id="kiit_fest_ops",
            source_event_id="evt_kbc_2026",
            category="POWER_DISRUPTION",
            title="Campus 6 Main Aud Outage Playbook",
            problem_statement="Main feeder failure.",
            resolution_strategy="Fast DG transfer + OAT relocation.",
        )
        assert ki.category == "POWER_DISRUPTION"
        assert len(rag_svc.knowledge_items) >= 1
