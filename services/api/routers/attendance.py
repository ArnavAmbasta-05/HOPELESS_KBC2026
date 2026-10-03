"""KoreX API — Attendance & Live Occupancy Router (Sprint 7, ATT-001..009, TAD §18)."""

from __future__ import annotations

import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from packages.contracts.attendance import (
    AttendanceCredential,
    AttendanceRecord,
    CredentialType,
    ReconciliationReport,
    ScanIngestRequest,
    SessionOccupancySignal,
)
from packages.contracts.auth import AuthUser
from packages.contracts.envelope import ResponseEnvelope, make_success_envelope
from services.api.auth.dependencies import get_current_user
from services.api.auth.rbac import Permission, require_permission
from services.workers.attendance.credentials import (
    AttendanceCredentialService,
    ExpiredCredentialTokenError,
    InvalidCredentialTokenError,
)
from services.workers.attendance.ingest import ScanIngestService
from services.workers.attendance.reconcile import AttendanceReconciler
from services.workers.attendance.replay import OfflineScanReplayEngine

router = APIRouter(prefix="/api/v1/attendance", tags=["Attendance & Occupancy"])

_credential_service = AttendanceCredentialService()
_ingest_service = ScanIngestService(credential_service=_credential_service)
_replay_engine = OfflineScanReplayEngine(ingest_service=_ingest_service)
_reconciler = AttendanceReconciler()


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class IssueCredentialRequest(BaseModel):
    participant_id: str = Field(..., description="Participant ID")
    event_id: str = Field(default="evt_kbc2026", description="Event ID")
    session_id: str | None = Field(default=None, description="Optional scoped session ID")
    lifetime_hours: int = Field(default=12, description="Token lifetime in hours")
    credential_type: CredentialType = Field(default=CredentialType.QR, description="QR or NFC")


class ReplayBatchRequest(BaseModel):
    scans: list[ScanIngestRequest] = Field(default_factory=list, description="List of queued offline scans")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/credentials",
    response_model=ResponseEnvelope[AttendanceCredential],
    summary="Issue a signed, opaque QR/NFC credential token",
)
async def issue_credential(
    request: IssueCredentialRequest,
    current_user: AuthUser = Depends(require_permission(Permission.ATTENDANCE_READ)),
) -> ResponseEnvelope[AttendanceCredential]:
    """Issues HMAC-signed opaque attendance token."""
    cred = _credential_service.issue_credential(
        participant_id=request.participant_id,
        event_id=request.event_id,
        session_id=request.session_id,
        lifetime_hours=request.lifetime_hours,
        credential_type=request.credential_type,
    )
    return make_success_envelope(data=cred, request_id=str(uuid.uuid4()))


@router.post(
    "/scan",
    response_model=ResponseEnvelope[dict[str, Any]],
    summary="Ingest check-in scan with deduplication and validation",
)
async def ingest_scan(
    request: ScanIngestRequest,
    current_user: AuthUser = Depends(require_permission(Permission.ATTENDANCE_SCAN)),
) -> ResponseEnvelope[dict[str, Any]]:
    """Ingests and validates check-in scan."""
    try:
        record, is_dup = _ingest_service.ingest_scan(request)
    except InvalidCredentialTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    except ExpiredCredentialTokenError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return make_success_envelope(
        data={"record": record, "is_duplicate": is_dup, "status": "VERIFIED"},
        request_id=str(uuid.uuid4()),
    )


@router.post(
    "/replay",
    response_model=ResponseEnvelope[dict[str, Any]],
    summary="Replay offline scan queue with duplicate suppression",
)
async def replay_offline_scans(
    request: ReplayBatchRequest,
    current_user: AuthUser = Depends(require_permission(Permission.ATTENDANCE_SCAN)),
) -> ResponseEnvelope[dict[str, Any]]:
    """Replays queued offline scans safely without duplicating counts."""
    result = _replay_engine.replay_batch(request.scans)
    return make_success_envelope(data=result, request_id=str(uuid.uuid4()))


@router.get(
    "/occupancy/{session_id}",
    response_model=ResponseEnvelope[SessionOccupancySignal],
    summary="Get privacy-preserving session occupancy signal for crowd control (AT-05)",
)
async def get_session_occupancy(
    session_id: str,
    venue_id: str = Query(default="ven_oat", description="Venue ID for capacity evaluation"),
    current_user: AuthUser = Depends(require_permission(Permission.ATTENDANCE_READ)),
) -> ResponseEnvelope[SessionOccupancySignal]:
    """Returns real-time session headcount and occupancy ratio without participant PII."""
    signal = _ingest_service.get_occupancy_signal(session_id=session_id, venue_id=venue_id)
    return make_success_envelope(data=signal, request_id=str(uuid.uuid4()))


# ---------------------------------------------------------------------------
# Participant Check-In & Excel Roster Store
# ---------------------------------------------------------------------------
from datetime import datetime, timezone
import io
import csv
from fastapi.responses import StreamingResponse
from packages.contracts.attendance import (
    ParticipantRegistrationRecord,
    ParticipantCheckInRequest,
)

# Seed with initial realistic records for KBC 2026 Conclave
_participant_roster: dict[str, ParticipantRegistrationRecord] = {
    "rec_001": ParticipantRegistrationRecord(
        record_id="rec_001",
        event_id="evt_kbc2026",
        full_name="Arnav Ambasta",
        roll_no="21051982",
        email="arnav.ambasta@kiit.ac.in",
        phone="+91 98765 43210",
        institution="KIIT School of Computer Engineering",
        session_id="ses_opening",
        session_name="Opening Ceremony & Keynote",
        venue_id="ven_oat",
        venue_name="Open Air Theatre (Campus 6)",
        check_in_time="2026-03-15T08:32:14Z",
        check_in_time_ist="15-03-2026 14:02:14 IST",
        status="CONFIRMED_PRESENT",
        qr_token="qr_kbc2026_arnav_ses_opening",
        notes="VIP Guest / Speaker delegate",
    ),
    "rec_002": ParticipantRegistrationRecord(
        record_id="rec_002",
        event_id="evt_kbc2026",
        full_name="Priya Sharma",
        roll_no="22053411",
        email="priya.sharma@kiit.ac.in",
        phone="+91 98123 45678",
        institution="KIIT School of Electronics Engineering",
        session_id="ses_opening",
        session_name="Opening Ceremony & Keynote",
        venue_id="ven_oat",
        venue_name="Open Air Theatre (Campus 6)",
        check_in_time="2026-03-15T08:41:05Z",
        check_in_time_ist="15-03-2026 14:11:05 IST",
        status="CONFIRMED_PRESENT",
        qr_token="qr_kbc2026_priya_ses_opening",
        notes="General Track",
    ),
    "rec_003": ParticipantRegistrationRecord(
        record_id="rec_003",
        event_id="evt_kbc2026",
        full_name="Rohit Verma",
        roll_no="KBC-IITKGP-442",
        email="rohit.verma@iitkgp.ac.in",
        phone="+91 97456 12389",
        institution="IIT Kharagpur",
        session_id="ses_keynote_ai",
        session_name="AI in Event Operations",
        venue_id="ven_aud_c7",
        venue_name="Auditorium (Campus 7)",
        check_in_time="2026-03-15T09:12:40Z",
        check_in_time_ist="15-03-2026 14:42:40 IST",
        status="CONFIRMED_PRESENT",
        qr_token="qr_kbc2026_rohit_ses_keynote_ai",
        notes="Hackathon Finalist",
    ),
    "rec_004": ParticipantRegistrationRecord(
        record_id="rec_004",
        event_id="evt_kbc2026",
        full_name="Sneha Pattnaik",
        roll_no="23058892",
        email="sneha.p@kiit.ac.in",
        phone="+91 99371 88234",
        institution="KIIT School of Biotechnology",
        session_id="ses_panel_tech",
        session_name="Future of Tech Panel",
        venue_id="ven_hall_c13",
        venue_name="Conference Hall (Campus 13)",
        check_in_time="2026-03-15T09:30:19Z",
        check_in_time_ist="15-03-2026 15:00:19 IST",
        status="CONFIRMED_PRESENT",
        qr_token="qr_kbc2026_sneha_ses_panel_tech",
        notes="Student Delegate",
    ),
}


@router.post(
    "/check-in",
    response_model=ResponseEnvelope[ParticipantRegistrationRecord],
    summary="Submit participant QR scan & registration form, marking instant attendance",
)
async def submit_participant_checkin(
    request: ParticipantCheckInRequest,
) -> ResponseEnvelope[ParticipantRegistrationRecord]:
    """Records participant check-in, marks attendance timestamp, and increments live venue occupancy."""
    now_utc = datetime.now(timezone.utc)
    ist_str = now_utc.strftime("%d-%m-%Y %H:%M:%S IST")
    
    rec_id = f"rec_{uuid.uuid4().hex[:8]}"
    record = ParticipantRegistrationRecord(
        record_id=rec_id,
        event_id="evt_kbc2026",
        full_name=request.full_name.strip(),
        roll_no=request.roll_no.strip(),
        email=request.email.strip(),
        phone=request.phone.strip(),
        institution=request.institution.strip() or "KIIT Deemed to be University",
        session_id=request.session_id,
        session_name=request.session_name,
        venue_id=request.venue_id,
        venue_name=request.venue_name,
        check_in_time=now_utc.isoformat(),
        check_in_time_ist=ist_str,
        status="CONFIRMED_PRESENT",
        qr_token=request.qr_token or f"qr_token_{rec_id}",
        notes=request.notes.strip(),
    )
    _participant_roster[rec_id] = record

    # Update session headcount in ingest service
    _ingest_service.session_headcounts[request.session_id] = (
        _ingest_service.session_headcounts.get(request.session_id, 0) + 1
    )

    return make_success_envelope(data=record, request_id=str(uuid.uuid4()))


@router.get(
    "/records",
    response_model=ResponseEnvelope[list[ParticipantRegistrationRecord]],
    summary="List all participant registration & attendance records",
)
async def list_attendance_records(
    session_id: str | None = Query(default=None, description="Filter by session ID"),
    search: str | None = Query(default=None, description="Search by name, roll no or institution"),
) -> ResponseEnvelope[list[ParticipantRegistrationRecord]]:
    """Returns all marked attendance records with optional search and session filter."""
    records = list(_participant_roster.values())
    if session_id:
        records = [r for r in records if r.session_id == session_id]
    if search:
        s = search.lower()
        records = [
            r for r in records
            if s in r.full_name.lower() or s in r.roll_no.lower() or s in r.institution.lower() or s in r.email.lower()
        ]
    
    # Sort latest first
    records.sort(key=lambda r: r.check_in_time, reverse=True)
    return make_success_envelope(data=records, request_id=str(uuid.uuid4()))


@router.get(
    "/export-excel",
    summary="Export verified participant attendance roster as Excel-compatible spreadsheet",
)
async def export_attendance_excel(
    session_id: str | None = Query(default=None, description="Filter by session ID"),
) -> StreamingResponse:
    """Generates an RFC 4180 Excel-compatible CSV spreadsheet with UTF-8 BOM for Microsoft Excel."""
    records = list(_participant_roster.values())
    if session_id:
        records = [r for r in records if r.session_id == session_id]
    records.sort(key=lambda r: r.check_in_time, reverse=True)

    output = io.StringIO()
    # Write UTF-8 BOM so Excel opens it with perfect character encoding
    output.write("\ufeff")
    
    writer = csv.writer(output, lineterminator="\r\n")
    # Column Headers
    writer.writerow([
        "Record ID",
        "Attendance Time (IST)",
        "Full Name",
        "Roll No / Reg ID",
        "Email Address",
        "Phone Number",
        "Institution / University",
        "Session Name",
        "Venue / Gate",
        "Attendance Status",
        "QR Token Hash",
        "Notes / Track",
    ])

    for r in records:
        writer.writerow([
            r.record_id,
            r.check_in_time_ist or r.check_in_time,
            r.full_name,
            r.roll_no,
            r.email,
            r.phone,
            r.institution,
            r.session_name,
            r.venue_name,
            r.status,
            r.qr_token,
            r.notes,
        ])

    csv_data = output.getvalue().encode("utf-8-sig")
    now_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"KBC2026_Attendance_Roster_{now_str}.csv"

    return StreamingResponse(
        io.BytesIO(csv_data),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache",
        },
    )
