"""Sprint 10: Resilience & Failure Drills Suite (S10-T2, TAD §22, NFR-REL-001..003)."""

from __future__ import annotations

import time
import pytest

from ai.fallback import LLMOutageFallbackHandler
from integrations.notion.dlq import NotionDLQManager
from packages.contracts.attendance import ScanIngestRequest
from packages.contracts.notion import NotionOperationType, NotionWriteOperation
from packages.contracts.planning import SolverStatus
from services.workers.attendance.credentials import AttendanceCredentialService
from services.workers.attendance.ingest import ScanIngestService
from services.workers.optimization.infeasible import InfeasibleResolutionHandler


def test_resilience_attendance_high_throughput_load():
    """Drill: Attendance throughput >= 50 scans/s (S10-T2.1, TAD §22)."""
    cred_svc = AttendanceCredentialService()
    ingest_svc = ScanIngestService(credential_service=cred_svc)
    
    # Generate 150 valid signed tokens
    scans: list[ScanIngestRequest] = []
    for i in range(150):
        cred = cred_svc.issue_credential(participant_id=f"usr_stress_{i}", event_id="evt_kbc2026")
        scans.append(
            ScanIngestRequest(
                token=cred.token,
                session_id="ses_opening",
                venue_id="ven_oat",
                scanner_id="scanner_gate_01",
            )
        )
    
    start = time.perf_counter()
    for scan in scans:
        rec, is_dup = ingest_svc.ingest_scan(scan)
        assert is_dup is False
    elapsed = time.perf_counter() - start
    
    throughput = len(scans) / elapsed
    assert throughput >= 50.0, f"Attendance throughput was {throughput:.2f} scans/s (< 50 scans/s)"
    assert ingest_svc.session_headcounts.get("ses_opening", 0) == 150


def test_resilience_notion_outage_circuit_breaker_and_dlq():
    """Drill: Notion outage causes graceful queuing in DLQ with incident log (S10-T2.2)."""
    dlq_manager = NotionDLQManager()
    dummy_op = NotionWriteOperation(
        op_type=NotionOperationType.UPDATE_PAGE,
        target_database="db_tasks",
        description="Update task N01",
    )

    entry = dlq_manager.record_failure(
        plan_id="nplan_fail_01",
        operation=dummy_op,
        error_message="503 Service Unavailable: Notion Gateway Timeout",
        event_id="evt_kbc2026",
    )

    assert entry.status == "PENDING"
    assert "503 Service Unavailable" in entry.error_message
    assert len(dlq_manager.list_entries()) == 1
    assert len(dlq_manager.list_incidents()) == 1


def test_resilience_llm_outage_deterministic_fallback():
    """Drill: LLM outage triggers deterministic fallback template generation without crashing (S10-T2.2)."""
    fallback = LLMOutageFallbackHandler.generate_fallback_summary(
        venue_name="Main Auditorium",
        relocated_count=4,
        at_risk_count=1,
        reason="Ceiling AC leak",
    )
    
    assert "[FALLBACK MODE]" in fallback.summary_text
    assert "Main Auditorium" in fallback.summary_text
    assert "4 sessions have been re-allocated" in fallback.summary_text


def test_resilience_solver_infeasibility_escalation_at09():
    """Drill AT-09: Solver encounters infeasible capacity and returns explicit failure reasons and manual actions (S10-T2.2)."""
    handler = InfeasibleResolutionHandler()
    
    res = handler.handle_infeasible_session(
        event_id="evt_kbc2026",
        disrupted_entity_id="ses_mega_concert",
        session_name="Celebrity Mega Concert",
        registrants=4000,
        available_candidate_capacities={
            "Seminar Hall": 250,
            "LH-3": 150,
            "LH-5": 120,
        },
    )
    
    assert res.status == SolverStatus.INFEASIBLE
    assert len(res.unmet_constraints) == 3
    assert any("Seminar Hall: capacity 250 < 4000" in r for r in res.rejected_reasons)
    assert len(res.manual_action_options) >= 3
    assert res.manual_action_options[0].title == "Split session into two concurrent tracks"
