"""Attendance & Live Occupancy Contracts (Sprint 7, ATT-001..009, TAD §18)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from pydantic import BaseModel, Field


class CredentialType(StrEnum):
    QR = "qr"
    NFC = "nfc"


class AttendanceCredential(BaseModel):
    """Cryptographically signed opaque participant credential token."""
    credential_id: str = Field(default_factory=lambda: f"cred_{uuid.uuid4().hex[:8]}")
    token: str  # Signed JWT or HMAC-SHA256 opaque string
    event_id: str
    session_id: str | None = None
    participant_id: str
    expires_at: str
    credential_type: CredentialType = CredentialType.QR


class ScanIngestRequest(BaseModel):
    """Scan event ingested from mobile PWA or scanner."""
    scan_id: str = Field(default_factory=lambda: f"scn_{uuid.uuid4().hex[:8]}")
    token: str
    session_id: str
    venue_id: str
    scanner_id: str = "scanner_gate_01"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    idempotency_key: str | None = None


class AttendanceRecord(BaseModel):
    """Verified persistent attendance record (RULE-07)."""
    attendance_id: str = Field(default_factory=lambda: f"att_{uuid.uuid4().hex[:8]}")
    event_id: str
    session_id: str
    participant_id: str
    venue_id: str
    verified_at: str
    scanner_id: str
    idempotency_key: str


class SessionOccupancySignal(BaseModel):
    """Privacy-preserving occupancy feed exposed to crowd control without PII (ATT-007, AT-05)."""
    session_id: str
    venue_id: str
    venue_name: str
    venue_capacity: int
    current_headcount: int
    occupancy_ratio: float  # headcount / capacity
    status: str  # NORMAL, NEAR_CAPACITY, SURGE_CAPACITY
    last_updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ParticipantRegistrationRecord(BaseModel):
    """Participant registration & check-in record for Excel export & attendance marking."""
    record_id: str = Field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:8]}")
    event_id: str = "evt_kbc2026"
    full_name: str
    roll_no: str
    email: str
    phone: str
    institution: str
    session_id: str
    session_name: str
    venue_id: str
    venue_name: str
    check_in_time: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    check_in_time_ist: str = ""
    status: str = "CONFIRMED_PRESENT"
    qr_token: str = ""
    notes: str = ""


class ParticipantCheckInRequest(BaseModel):
    """Payload submitted when scanning QR and filling check-in form."""
    full_name: str
    roll_no: str
    email: str
    phone: str
    institution: str = "KIIT Deemed to be University"
    session_id: str = "ses_opening"
    session_name: str = "Opening Ceremony & Keynote"
    venue_id: str = "ven_oat"
    venue_name: str = "Open Air Theatre (Campus 6)"
    qr_token: str = ""
    notes: str = ""


class ReconciliationReport(BaseModel):
    """Report comparing registered roster vs actual verified scans (ATT-005)."""
    session_id: str
    session_name: str
    total_registered: int
    total_attended: int
    no_shows_count: int
    late_arrivals_count: int
    reconciliation_ratio: float
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
