"""Scan Ingest & Occupancy Engine (Sprint 7, S7-T4, ATT-003/006/007, AT-05, TAD §18).

Processes scan events:
- Validates signed token
- Enforces scan idempotency key = credential + session + scan_window
- Updates near-real-time session headcount
- Emits SessionOccupancySignal for crowd control without exposing identity
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from packages.contracts.attendance import (
    AttendanceRecord,
    ScanIngestRequest,
    SessionOccupancySignal,
)
from services.workers.attendance.credentials import AttendanceCredentialService


class ScanIngestService:
    """Ingests check-in scans and computes real-time venue occupancy."""

    def __init__(self, credential_service: AttendanceCredentialService | None = None) -> None:
        self.credential_service = credential_service or AttendanceCredentialService()
        self.records: dict[str, AttendanceRecord] = {}
        self.idempotency_keys: set[str] = set()
        self.session_headcounts: dict[str, int] = {}
        self.venue_capacities: dict[str, int] = {
            "ven_oat": 600,
            "ven_aud_c7": 250,
            "ven_hall_c13": 120,
            "ven_main_aud": 1600,
        }
        self.venue_names: dict[str, str] = {
            "ven_oat": "Open Air Theatre (Campus 6)",
            "ven_aud_c7": "Auditorium (Campus 7)",
            "ven_hall_c13": "Conference Hall (Campus 13)",
            "ven_main_aud": "Main Auditorium (Campus 6)",
        }

    def ingest_scan(self, request: ScanIngestRequest) -> tuple[AttendanceRecord, bool]:
        """Ingest a scan. Returns (record, is_duplicate)."""
        # Step 1: Verify token signature and expiration
        payload = self.credential_service.verify_token(request.token)
        participant_id = payload["pid"]

        # Step 2: Formulate idempotency key (ATT-003)
        scan_window = request.timestamp[:13]  # Hourly scan window bucket
        idem_key = request.idempotency_key or f"idem_scan_{participant_id}_{request.session_id}_{scan_window}"

        # Deduplication check
        if idem_key in self.idempotency_keys:
            # Return existing record without double-counting
            existing = [r for r in self.records.values() if r.idempotency_key == idem_key]
            if existing:
                return existing[0], True

        self.idempotency_keys.add(idem_key)

        record = AttendanceRecord(
            event_id=payload.get("eid", "evt_kbc2026"),
            session_id=request.session_id,
            participant_id=participant_id,
            venue_id=request.venue_id,
            verified_at=request.timestamp,
            scanner_id=request.scanner_id,
            idempotency_key=idem_key,
        )
        self.records[record.attendance_id] = record

        # Increment headcount
        self.session_headcounts[request.session_id] = self.session_headcounts.get(request.session_id, 0) + 1

        return record, False

    def get_occupancy_signal(self, session_id: str, venue_id: str) -> SessionOccupancySignal:
        """Compute privacy-preserving occupancy signal for crowd control (ATT-007, AT-05)."""
        headcount = self.session_headcounts.get(session_id, 0)
        capacity = self.venue_capacities.get(venue_id, 500)
        ratio = round(headcount / capacity, 2) if capacity > 0 else 0.0

        if ratio >= 0.95:
            status = "SURGE_CAPACITY"
        elif ratio >= 0.80:
            status = "NEAR_CAPACITY"
        else:
            status = "NORMAL"

        return SessionOccupancySignal(
            session_id=session_id,
            venue_id=venue_id,
            venue_name=self.venue_names.get(venue_id, "Venue"),
            venue_capacity=capacity,
            current_headcount=headcount,
            occupancy_ratio=ratio,
            status=status,
        )
