"""Integration and Golden Scenario Tests for Sprint 7 (Participant Operations — Notifications + Attendance + PWA).

Validates:
- S7-T1: Cohort Derivation (380/230/180/390) & Grounded Message Drafts (COM-001..003, RULE-02)
- S7-T2: Mass Dispatch Approval Gate & Multi-Channel Delivery Tracking (COM-005/006/008, RULE-03)
- S7-T3: Stale Communication & Directional Signage Detector (FR-NOTIFY-005, COM-007)
- S7-T4: Signed Attendance Credentials, Forgery Defense, Idempotent Scan Ingest & AT-05 Occupancy Signals (ATT-001..007, AT-05)
- S7-T5: Offline Scan Queue Replay & Attendance Reconciliation without Registration Mutation (ATT-004/005, RULE-07)
- S7-API: HTTP REST endpoints for notifications and attendance APIs
"""

from __future__ import annotations

import pytest
import httpx

from packages.contracts.attendance import CredentialType, ScanIngestRequest
from packages.contracts.notifications import ChannelType, DeliveryStatus
from services.api.auth.providers import DevLoginProvider
from services.api.main import app
from services.workers.attendance.credentials import (
    AttendanceCredentialService,
    ExpiredCredentialTokenError,
    InvalidCredentialTokenError,
)
from services.workers.attendance.ingest import ScanIngestService
from services.workers.attendance.reconcile import AttendanceReconciler
from services.workers.attendance.replay import OfflineScanReplayEngine
from services.workers.notifications.service import (
    MassDispatchRequiresApprovalError,
    NotificationService,
)


class TestNotificationCohortsAndDrafts:
    """Tests for S7-T1 (COM-001..003, RULE-02)."""

    def test_golden_disruption_cohorts_derived(self) -> None:
        service = NotificationService()
        cohorts = service.get_impacted_cohorts()

        assert len(cohorts) == 5
        cohort_counts = {c.target_entity_id: c.recipient_count for c in cohorts}
        assert cohort_counts["ses_opening"] == 380
        assert cohort_counts["ses_keynote_ai"] == 230
        assert cohort_counts["ses_panel_tech"] == 180
        assert cohort_counts["ses_valedictory"] == 390
        assert cohort_counts["ven_main_aud"] == 5

    def test_grounded_drafts_contain_mandatory_facts_and_ai_label(self) -> None:
        service = NotificationService()
        drafts = service.get_drafts()

        assert len(drafts) == 4
        for d in drafts:
            # Mandated fact fields (COM-003)
            assert d.old_state != ""
            assert d.new_state != ""
            assert d.effective_time != ""
            assert d.action_required != ""
            assert "AI-GENERATED, unverified narrative" in d.ai_label
            assert d.is_ai_draft is True
            assert d.approved is False


class TestMassDispatchApprovalGateAndChannels:
    """Tests for S7-T2 (COM-005/006/008, RULE-03)."""

    @pytest.mark.asyncio
    async def test_unapproved_mass_dispatch_blocked_by_approval_gate(self) -> None:
        service = NotificationService()
        drafts = service.get_drafts()
        target_draft = drafts[0]

        # Attempt dispatch without approval -> must fail (RULE-03, COM-008)
        with pytest.raises(MassDispatchRequiresApprovalError):
            await service.dispatch_notification(
                draft_id=target_draft.draft_id,
                channel=ChannelType.PUSH,
                is_approved=False,
            )

    @pytest.mark.asyncio
    async def test_approved_mass_dispatch_executes_with_deduplication(self) -> None:
        service = NotificationService()
        drafts = service.get_drafts()
        target_draft = drafts[0]

        # Approve draft
        service.approve_draft(target_draft.draft_id, approved_by="event_commander")
        assert target_draft.approved is True

        # Dispatch
        records = await service.dispatch_notification(
            draft_id=target_draft.draft_id,
            channel=ChannelType.PUSH,
            is_approved=True,
        )

        assert len(records) == 380
        assert records[0].status == DeliveryStatus.DELIVERED
        assert records[0].sent_at is not None

        # Dedup check: second dispatch produces 0 duplicates (COM-005)
        records_second = await service.dispatch_notification(
            draft_id=target_draft.draft_id,
            channel=ChannelType.PUSH,
            is_approved=True,
        )
        assert len(records_second) == 0


class TestStaleCommunicationsDetection:
    """Tests for S7-T3 (FR-NOTIFY-005, COM-007)."""

    def test_stale_comms_and_boards_flagged(self) -> None:
        service = NotificationService()
        stale_items = service.scan_stale_comms()

        assert len(stale_items) >= 3
        channels = [item.channel_or_location for item in stale_items]
        assert any("Instagram" in c for c in channels)
        assert any("Gate 1" in c for c in channels)
        assert any("Gate 3" in c for c in channels)


class TestAttendanceCredentialsAndScanIngest:
    """Tests for S7-T4 (ATT-001..007, AT-05)."""

    def test_credential_issuance_and_signature_verification(self) -> None:
        cred_service = AttendanceCredentialService()
        cred = cred_service.issue_credential(
            participant_id="part_op_001",
            session_id="ses_opening",
            lifetime_hours=12,
        )

        assert cred.token != ""
        payload = cred_service.verify_token(cred.token)
        assert payload["pid"] == "part_op_001"
        assert payload["sid"] == "ses_opening"

    def test_tampered_and_expired_credential_tokens_rejected(self) -> None:
        cred_service = AttendanceCredentialService()
        cred = cred_service.issue_credential(participant_id="part_op_001")

        # Tampered token
        tampered_token = cred.token[:-5] + "XXXXX"
        with pytest.raises(InvalidCredentialTokenError):
            cred_service.verify_token(tampered_token)

        # Expired token
        expired_cred = cred_service.issue_credential(participant_id="part_op_001", lifetime_hours=-1)
        with pytest.raises(ExpiredCredentialTokenError):
            cred_service.verify_token(expired_cred.token)

    def test_idempotent_scan_ingest_suppresses_duplicates(self) -> None:
        cred_service = AttendanceCredentialService()
        ingest_service = ScanIngestService(credential_service=cred_service)

        cred = cred_service.issue_credential(participant_id="part_op_001", session_id="ses_opening")

        req = ScanIngestRequest(
            token=cred.token,
            session_id="ses_opening",
            venue_id="ven_oat",
            timestamp="2026-03-15T08:45:00Z",
        )

        # First scan
        rec1, is_dup1 = ingest_service.ingest_scan(req)
        assert is_dup1 is False
        assert rec1.participant_id == "part_op_001"
        assert ingest_service.session_headcounts["ses_opening"] == 1

        # Second identical scan -> duplicate suppressed
        rec2, is_dup2 = ingest_service.ingest_scan(req)
        assert is_dup2 is True
        assert rec2.attendance_id == rec1.attendance_id
        assert ingest_service.session_headcounts["ses_opening"] == 1  # No double counting


class TestOfflineScanReplayAndReconciliation:
    """Tests for S7-T5 (ATT-004/005, RULE-07)."""

    def test_offline_batch_replay_with_deduplication(self) -> None:
        cred_service = AttendanceCredentialService()
        ingest_service = ScanIngestService(credential_service=cred_service)
        replay_engine = OfflineScanReplayEngine(ingest_service=ingest_service)

        # Generate 5 scans (including 1 duplicate)
        scans = []
        for i in range(1, 5):
            c = cred_service.issue_credential(participant_id=f"part_offline_{i}", session_id="ses_opening")
            scans.append(
                ScanIngestRequest(
                    token=c.token,
                    session_id="ses_opening",
                    venue_id="ven_oat",
                    timestamp="2026-03-15T08:50:00Z",
                )
            )
        # Add duplicate
        scans.append(scans[0])

        result = replay_engine.replay_batch(scans)
        assert result["total_submitted"] == 5
        assert result["new_records_created"] == 4
        assert result["duplicates_suppressed"] == 1
        assert ingest_service.session_headcounts["ses_opening"] == 4

    def test_reconciliation_produces_reports_without_mutating_registration(self) -> None:
        reconciler = AttendanceReconciler()
        report = reconciler.reconcile_session(
            session_id="ses_opening",
            session_name="Opening Ceremony",
            registered_count=380,
            attended_count=360,
            late_arrivals=15,
        )

        assert report.total_registered == 380
        assert report.total_attended == 360
        assert report.no_shows_count == 20
        assert report.late_arrivals_count == 15
        assert report.reconciliation_ratio == 0.95


class TestAT05OccupancySignalFeed:
    """Tests for AT-05 occupancy signals."""

    def test_occupancy_signal_transitions(self) -> None:
        cred_service = AttendanceCredentialService()
        ingest_service = ScanIngestService(credential_service=cred_service)

        # Venue OAT capacity = 600
        # 1. Normal state (100 attendees -> 17%)
        ingest_service.session_headcounts["ses_opening"] = 100
        sig1 = ingest_service.get_occupancy_signal("ses_opening", "ven_oat")
        assert sig1.status == "NORMAL"
        assert sig1.occupancy_ratio == 0.17

        # 2. Near capacity (500 attendees -> 83%)
        ingest_service.session_headcounts["ses_opening"] = 500
        sig2 = ingest_service.get_occupancy_signal("ses_opening", "ven_oat")
        assert sig2.status == "NEAR_CAPACITY"
        assert sig2.occupancy_ratio == 0.83

        # 3. Surge capacity (580 attendees -> 97%)
        ingest_service.session_headcounts["ses_opening"] = 580
        sig3 = ingest_service.get_occupancy_signal("ses_opening", "ven_oat")
        assert sig3.status == "SURGE_CAPACITY"
        assert sig3.occupancy_ratio == 0.97


class TestParticipantHTTPAPI:
    """HTTP REST endpoint tests for Sprint 7 APIs."""

    @pytest.mark.asyncio
    async def test_notifications_and_attendance_api_endpoints(self) -> None:
        provider = DevLoginProvider()
        token = provider.create_token(email="admin@kiit.ac.in", roles=["event_commander", "registration_lead"])
        headers = {"Authorization": f"Bearer {token}"}

        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. Cohorts API
            coh_resp = await client.get("/api/v1/notifications/cohorts", headers=headers)
            assert coh_resp.status_code == 200
            assert len(coh_resp.json()["data"]) == 5

            # 2. Drafts API
            drafts_resp = await client.get("/api/v1/notifications/drafts", headers=headers)
            assert drafts_resp.status_code == 200
            draft_id = drafts_resp.json()["data"][0]["draft_id"]

            # 3. Approve draft API
            app_resp = await client.post(f"/api/v1/notifications/drafts/{draft_id}/approve", headers=headers)
            assert app_resp.status_code == 200
            assert app_resp.json()["data"]["approved"] is True

            # 4. Dispatch API
            disp_resp = await client.post(
                "/api/v1/notifications/dispatch",
                json={"draft_id": draft_id, "channel": "push", "is_approved": True},
                headers=headers,
            )
            assert disp_resp.status_code == 200
            assert len(disp_resp.json()["data"]) == 380

            # 5. Stale comms API
            stale_resp = await client.get("/api/v1/notifications/stale", headers=headers)
            assert stale_resp.status_code == 200
            assert len(stale_resp.json()["data"]) >= 3

            # 6. Issue Attendance Credential API
            cred_resp = await client.post(
                "/api/v1/attendance/credentials",
                json={"participant_id": "part_http_01", "session_id": "ses_opening"},
                headers=headers,
            )
            assert cred_resp.status_code == 200
            cred_token = cred_resp.json()["data"]["token"]

            # 7. Ingest Scan API
            scan_resp = await client.post(
                "/api/v1/attendance/scan",
                json={
                    "token": cred_token,
                    "session_id": "ses_opening",
                    "venue_id": "ven_oat",
                },
                headers=headers,
            )
            assert scan_resp.status_code == 200
            assert scan_resp.json()["data"]["status"] == "VERIFIED"

            # 8. Occupancy Signal API
            occ_resp = await client.get("/api/v1/attendance/occupancy/ses_opening?venue_id=ven_oat", headers=headers)
            assert occ_resp.status_code == 200
            assert occ_resp.json()["data"]["current_headcount"] >= 1
