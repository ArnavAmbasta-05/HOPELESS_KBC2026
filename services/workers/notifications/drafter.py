"""Grounded Notification Drafter (Sprint 7, S7-T1.2, COM-002/003, RULE-02).

Ensures all communication drafts strictly include approved operational facts:
- old_state (e.g. "Main Auditorium (Campus 6)")
- new_state (e.g. "Open Air Theatre (Campus 6)")
- effective_time (e.g. "09:00 AM")
- action_required (e.g. "Proceed directly to Open Air Theatre. Doors open at 08:45 AM.")
- labeled as AI-GENERATED until approved.
"""

from __future__ import annotations

from packages.contracts.notifications import GroundedMessageDraft


class GroundedMessageDrafter:
    """Generates strictly grounded participant notifications."""

    def create_venue_relocation_draft(
        self,
        cohort_id: str,
        session_name: str,
        old_venue: str,
        new_venue: str,
        effective_time: str,
        action_required: str,
    ) -> GroundedMessageDraft:
        """Create a structured relocation notification draft."""
        message_text = (
            f"IMPORTANT VENUE UPDATE: '{session_name}' has been relocated from {old_venue} to {new_venue} "
            f"effective {effective_time}. {action_required}"
        )

        return GroundedMessageDraft(
            cohort_id=cohort_id,
            session_name=session_name,
            old_state=old_venue,
            new_state=new_venue,
            effective_time=effective_time,
            action_required=action_required,
            message_text=message_text,
            is_ai_draft=True,
            ai_label="AI-GENERATED, unverified narrative; facts above are the source of truth",
            approved=False,
        )

    def generate_golden_disruption_drafts(self) -> list[GroundedMessageDraft]:
        """Generate the standard 4 drafts for golden relocation tasks N11-N14."""
        return [
            self.create_venue_relocation_draft(
                cohort_id="coh_ses_opening",
                session_name="Opening Ceremony & Keynote",
                old_venue="Main Auditorium (Campus 6)",
                new_venue="Open Air Theatre (Campus 6)",
                effective_time="09:00 AM",
                action_required="Please proceed directly to Open Air Theatre (Gate 1 entry).",
            ),
            self.create_venue_relocation_draft(
                cohort_id="coh_ses_keynote_ai",
                session_name="AI in Event Operations",
                old_venue="Main Auditorium (Campus 6)",
                new_venue="Auditorium (Campus 7)",
                effective_time="11:30 AM",
                action_required="Take Campus Shuttle 1 or 5-minute walkway to Campus 7 Auditorium.",
            ),
            self.create_venue_relocation_draft(
                cohort_id="coh_ses_panel_tech",
                session_name="Future of Tech Panel",
                old_venue="Main Auditorium (Campus 6)",
                new_venue="Conference Hall (Campus 13)",
                effective_time="02:00 PM",
                action_required="Proceed to Campus 13 Conference Hall via Main Link.",
            ),
            self.create_venue_relocation_draft(
                cohort_id="coh_ses_valedictory",
                session_name="Valedictory & Awards",
                old_venue="Main Auditorium (Campus 6)",
                new_venue="Open Air Theatre (Campus 6)",
                effective_time="05:00 PM",
                action_required="Awards ceremony will take place at Open Air Theatre. Seating begins 04:30 PM.",
            ),
        ]
