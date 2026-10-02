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


@router.get(
    "/reconcile/{session_id}",
    response_model=ResponseEnvelope[ReconciliationReport],
    summary="Reconcile session registration roster vs actual scans (ATT-005)",
)
async def reconcile_session_attendance(
    session_id: str,
    session_name: str = Query(default="Opening Ceremony", description="Session Name"),
    registered_count: int = Query(default=380, description="Total registered"),
    current_user: AuthUser = Depends(require_permission(Permission.ATTENDANCE_READ)),
) -> ResponseEnvelope[ReconciliationReport]:
    """Computes attended vs no-show ratio without modifying registration database (RULE-07)."""
    attended = _ingest_service.session_headcounts.get(session_id, 0)
    report = _reconciler.reconcile_session(
        session_id=session_id,
        session_name=session_name,
        registered_count=registered_count,
        attended_count=attended,
    )
    return make_success_envelope(data=report, request_id=str(uuid.uuid4()))
