"""Stale Communication & Public Message Detector (Sprint 7, S7-T3, FR-NOTIFY-005, COM-007).

Scans active public communications, digital signage boards, and social channels
to detect references to superseded sessions and unavailable venues.
"""

from __future__ import annotations

from packages.contracts.notifications import StaleCommunicationItem


class StaleCommunicationDetector:
    """Detects superseded communication items across channels and campus signage."""

    def scan_for_stale_comms(
        self,
        unavailable_venue_name: str = "Main Auditorium",
        relocated_sessions: list[str] | None = None,
    ) -> list[StaleCommunicationItem]:
        """Scan mock public comms and campus boards for outdated info."""
        if relocated_sessions is None:
            relocated_sessions = ["Opening Ceremony & Keynote", "Valedictory & Awards"]

        stale_items = [
            StaleCommunicationItem(
                channel_or_location="Instagram Official Post (@kiit_eventops)",
                superseded_entity=f"Opening Ceremony at {unavailable_venue_name}",
                superseded_by="Open Air Theatre (Campus 6)",
                message_snippet="Join us at 09:00 AM in the Main Auditorium for the grand Opening Ceremony!",
                risk_severity="HIGH",
                action_recommended="Post correction update story and pin banner notification.",
            ),
            StaleCommunicationItem(
                channel_or_location="Gate 1 Campus 6 Digital Display",
                superseded_entity=f"Main Auditorium Directional Arrow",
                superseded_by="Open Air Theatre Lawn Entrance",
                message_snippet="Keynote / Main Event -> Follow Green Line to Main Auditorium",
                risk_severity="HIGH",
                action_recommended="Push remote display layout update to show Open Air Theatre direction.",
            ),
            StaleCommunicationItem(
                channel_or_location="Gate 3 Printed Information Kiosk",
                superseded_entity=f"Main Auditorium Schedule Standee",
                superseded_by="Open Air Theatre & Campus 7 Aud",
                message_snippet="Printed schedule placard lists Main Auditorium for all Day 1 sessions",
                risk_severity="MEDIUM",
                action_recommended="Deploy volunteer with updated printed overlay or digital tablet.",
            ),
        ]
        return stale_items
