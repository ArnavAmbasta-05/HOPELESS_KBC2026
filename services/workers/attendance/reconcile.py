"""Attendance Reconciliation & Late Adjustment Auditor (Sprint 7, ATT-005, RULE-07).

Reconciles expected registration rosters with actual recorded scans.
Enforces RULE-07: Attendance records never silently mutate registration records.
Audits all manual adjustments or late corrections made by authorized operators.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from packages.contracts.attendance import ReconciliationReport


class AttendanceReconciler:
    """Reconciles session registration counts against scan verified headcounts."""

    def reconcile_session(
        self,
        session_id: str,
        session_name: str,
        registered_count: int,
        attended_count: int,
        late_arrivals: int = 0,
    ) -> ReconciliationReport:
        """Generate reconciliation report for a session."""
        no_shows = max(0, registered_count - attended_count)
        ratio = round(attended_count / registered_count, 2) if registered_count > 0 else 1.0

        return ReconciliationReport(
            session_id=session_id,
            session_name=session_name,
            total_registered=registered_count,
            total_attended=attended_count,
            no_shows_count=no_shows,
            late_arrivals_count=late_arrivals,
            reconciliation_ratio=ratio,
        )

    def record_manual_late_checkin(
        self,
        participant_id: str,
        session_id: str,
        operator_id: str,
        reason: str,
    ) -> dict[str, Any]:
        """Audits manual late check-in by operator (ATT-005)."""
        return {
            "audit_id": f"aud_att_{uuid.uuid4().hex[:8]}",
            "participant_id": participant_id,
            "session_id": session_id,
            "operator_id": operator_id,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "MANUAL_LATE_CHECKIN",
        }
